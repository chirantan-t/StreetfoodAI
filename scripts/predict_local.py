"""
Command-line inference script for predicting Indian street food from a local image file.
"""
import sys
import json
import argparse
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.inference.predictor import StreetFoodPredictor
from backend.app.services.nutrition_service import NutritionService

def predict_local_image(
    image_path: str,
    model_name: str = "mobilenet_v3_large",
    weights_path: str = None,
    serving_size: str = "Regular"
):
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image '{image_path}' not found.")
        return

    image = Image.open(path).convert("RGB")
    predictor = StreetFoodPredictor(model_name=model_name, weights_path=weights_path, auto_load_checkpoint=True)
    result = predictor.predict(image, top_k=5)

    nutrition_svc = NutritionService()
    nutrition = nutrition_svc.get_nutrition(result["predicted_food"], serving_size=serving_size)

    print("\n==========================================")
    print(f"StreetFoodAI Local Prediction")
    print(f"File: {path.name}")
    print(f"Model Architecture: {result['model_architecture']} ({result['weights_status']})")
    print("==========================================")
    print(f"Predicted Food:   {result['predicted_food']}")
    print(f"Confidence Score: {result['confidence'] * 100:.2f}%")
    print(f"Entropy:          {result['entropy']:.3f} nats")
    print(f"Uncertainty Flag: {result['is_uncertain']}")
    if result["rejection_reason"]:
        print(f"Rejection Note:   {result['rejection_reason']}")

    print("\nAlternative Candidates:")
    for c in result["top_candidates"]:
        print(f"  - {c['food_name']:<20}: {c['confidence'] * 100:.1f}%")

    print("\nNutritional Estimation:")
    print(f"  Serving:        {nutrition['serving_size']} ({nutrition['serving_weight_g']}g)")
    print(f"  Calories:       {nutrition['calories']} kcal")
    print(f"  Carbohydrates:  {nutrition['carbohydrates']} g")
    print(f"  Protein:        {nutrition['protein']} g")
    print(f"  Fat:            {nutrition['fat']} g")
    print(f"  Fiber:          {nutrition['fiber']} g")
    print(f"  Data Source:    {nutrition['data_source']}")
    print("==========================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Indian street food from local image")
    parser.add_argument("image", help="Path to input image file")
    parser.add_argument("--model", default="mobilenet_v3_large")
    parser.add_argument("--weights", default=None)
    parser.add_argument("--serving", default="Regular", choices=["Small", "Regular", "Large"])
    args = parser.parse_args()

    predict_local_image(
        image_path=args.image,
        model_name=args.model,
        weights_path=args.weights,
        serving_size=args.serving
    )
