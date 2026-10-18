from typing import List, Optional
from pydantic import BaseModel
from backend.app.schemas.nutrition import NutritionData

class CandidatePrediction(BaseModel):
    class_index: int
    food_name: str
    confidence: float

class PredictionResponse(BaseModel):
    predicted_food: str
    predicted_class_index: int
    raw_top_class: str
    confidence: float
    entropy: float
    is_uncertain: bool
    rejection_reason: Optional[str] = None
    top_candidates: List[CandidatePrediction]
    model_architecture: str
    weights_status: str
    serving_size: str
    nutrition: NutritionData
