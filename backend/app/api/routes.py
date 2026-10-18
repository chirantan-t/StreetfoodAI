"""
FastAPI Route Handlers for StreetFoodAI API.
Provides endpoints for health, prediction, Grad-CAM explainability,
nutritional lookup, history management, and analytical benchmarking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
import torch

from backend.app.database.session import get_db
from backend.app.database.models import PredictionRecord
from backend.app.schemas.health import HealthResponse
from backend.app.schemas.nutrition import NutritionData
from backend.app.schemas.prediction import PredictionResponse, CandidatePrediction
from backend.app.schemas.explain import ExplainResponse
from backend.app.schemas.history import HistoryCreate, HistoryResponse
from backend.app.utils.image_utils import validate_and_load_image
from backend.app.services.nutrition_service import NutritionService
from ml.inference.predictor import StreetFoodPredictor
from ml.explainability.gradcam import GradCAM, overlay_heatmap, image_to_base64
from ml.data.augmentation import get_raw_display_transforms

router = APIRouter(prefix="/api", tags=["StreetFoodAI API"])

# Singletons initialized at startup
_predictor: Optional[StreetFoodPredictor] = None
_nutrition_service: Optional[NutritionService] = None

def get_predictor() -> StreetFoodPredictor:
    global _predictor
    if _predictor is None:
        _predictor = StreetFoodPredictor(auto_load_checkpoint=True, confidence_threshold=0.40, entropy_threshold=2.40)
    else:
        _predictor.check_and_reload_weights()
    return _predictor

def get_nutrition_svc() -> NutritionService:
    global _nutrition_service
    if _nutrition_service is None:
        _nutrition_service = NutritionService()
    return _nutrition_service

# 1. Health Endpoint
@router.get("/health", response_model=HealthResponse)
def health_check(predictor: StreetFoodPredictor = Depends(get_predictor)):
    return HealthResponse(
        status="healthy",
        app_name="StreetFoodAI",
        version="1.0.0",
        model_architecture=predictor.model_name,
        model_weights_status=predictor.metadata.get("status", "unknown"),
        device=predictor.device,
        is_model_ready=predictor.model is not None,
        num_classes=predictor.num_classes,
        supported_classes=predictor.classes
    )

# 2. Supported Foods & Nutrition Database
@router.get("/foods")
def get_supported_foods(nutrition_svc: NutritionService = Depends(get_nutrition_svc)):
    return nutrition_svc.get_all_foods()

# 3. Nutrition lookup for specific food
@router.get("/nutrition/{food_name}", response_model=NutritionData)
def get_food_nutrition(
    food_name: str,
    serving_size: str = "Regular",
    nutrition_svc: NutritionService = Depends(get_nutrition_svc)
):
    data = nutrition_svc.get_nutrition(food_name, serving_size=serving_size)
    return NutritionData(**data)

# 4. Predict Food from Image
@router.post("/predict", response_model=PredictionResponse)
async def predict_food(
    image: UploadFile = File(...),
    serving_size: str = Form("Regular"),
    predictor: StreetFoodPredictor = Depends(get_predictor),
    nutrition_svc: NutritionService = Depends(get_nutrition_svc)
):
    pil_img = await validate_and_load_image(image)
    result = predictor.predict(pil_img, top_k=5)

    # Lookup nutrition for predicted category
    predicted_food_for_nutrition = result["predicted_food"]
    nutrition_info = nutrition_svc.get_nutrition(
        predicted_food_for_nutrition,
        serving_size=serving_size
    )

    return PredictionResponse(
        predicted_food=result["predicted_food"],
        predicted_class_index=result["predicted_class_index"],
        raw_top_class=result["raw_top_class"],
        confidence=result["confidence"],
        entropy=result["entropy"],
        is_uncertain=result["is_uncertain"],
        rejection_reason=result["rejection_reason"],
        top_candidates=[CandidatePrediction(**c) for c in result["top_candidates"]],
        model_architecture=result["model_architecture"],
        weights_status=result["weights_status"],
        serving_size=serving_size,
        nutrition=NutritionData(**nutrition_info)
    )

# 5. Explain via Grad-CAM
@router.post("/explain", response_model=ExplainResponse)
async def explain_prediction(
    image: UploadFile = File(...),
    target_class_index: Optional[int] = Form(None),
    predictor: StreetFoodPredictor = Depends(get_predictor)
):
    pil_img = await validate_and_load_image(image)

    # Prepare input tensor
    img_tensor = predictor.transform(pil_img).unsqueeze(0).to(predictor.device)

    try:
        model, target_layer = predictor.get_model_for_gradcam()
        gradcam = GradCAM(model=model, target_layer=target_layer)

        cam, class_idx, confidence = gradcam.generate_heatmap(
            input_tensor=img_tensor,
            target_class_idx=target_class_index
        )
        gradcam.remove_hooks()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grad-CAM generation failed: {str(e)}"
        )

    # Resize display image to 224x224 and overlay
    display_img = get_raw_display_transforms()(pil_img)
    overlay_img = overlay_heatmap(display_img, cam, alpha=0.55)
    overlay_base64 = image_to_base64(overlay_img)

    predicted_class_name = predictor.classes[class_idx]

    return ExplainResponse(
        predicted_class=predicted_class_name,
        target_class_index=class_idx,
        confidence=round(confidence, 4),
        heatmap_overlay_base64=overlay_base64,
        target_layer=str(target_layer)
    )

# 6. History Endpoints
@router.get("/history", response_model=List[HistoryResponse])
def get_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    records = db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return [HistoryResponse(**r.to_dict()) for r in records]

@router.post("/history", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
def create_history_record(
    item: HistoryCreate,
    db: Session = Depends(get_db)
):
    record = PredictionRecord(
        food_name=item.food_name,
        confidence=item.confidence,
        serving_size=item.serving_size,
        serving_weight_g=item.serving_weight_g,
        calories=item.calories,
        protein=item.protein,
        carbohydrates=item.carbohydrates,
        fat=item.fat,
        fiber=item.fiber,
        is_uncertain=item.is_uncertain,
        model_architecture=item.model_architecture,
        notes=item.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return HistoryResponse(**record.to_dict())

@router.delete("/history/{prediction_id}", status_code=status.HTTP_200_OK)
def delete_history_record(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record #{prediction_id} not found."
        )
    db.delete(record)
    db.commit()
    return {"message": f"Prediction record #{prediction_id} deleted successfully."}

# 7. Analytics and Benchmark Reports
@router.get("/analytics")
def get_analytics_data():
    """
    Returns authentic analytical and experimental benchmarking reports.
    """
    from pathlib import Path
    import json

    comparison_path = Path("results/reports/model_comparison.json")
    dataset_summary_path = Path("data/metadata/dataset_summary.json")

    comparison = {}
    if comparison_path.exists():
        with open(comparison_path, "r", encoding="utf-8") as f:
            comparison = json.load(f)

    dataset_summary = {}
    if dataset_summary_path.exists():
        with open(dataset_summary_path, "r", encoding="utf-8") as f:
            dataset_summary = json.load(f)

    return {
        "model_comparison": comparison.get("models", {}),
        "dataset_summary": dataset_summary,
        "status": "ready"
    }
