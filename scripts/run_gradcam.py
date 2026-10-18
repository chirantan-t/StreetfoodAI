"""
CLI tool to generate and save a Grad-CAM visual attention heatmap for an image.
"""
import sys
import argparse
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.inference.predictor import StreetFoodPredictor
from ml.explainability.gradcam import GradCAM, overlay_heatmap
from ml.data.augmentation import get_raw_display_transforms

def generate_local_gradcam(
    image_path: str,
    output_path: str = "results/plots/gradcam_output.jpg",
    model_name: str = "mobilenet_v3_large",
    weights_path: str = None
):
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image '{image_path}' not found.")
        return

    image = Image.open(path).convert("RGB")
    predictor = StreetFoodPredictor(model_name=model_name, weights_path=weights_path)
    img_tensor = predictor.transform(image).unsqueeze(0).to(predictor.device)

    model, target_layer = predictor.get_model_for_gradcam()
    gradcam = GradCAM(model=model, target_layer=target_layer)

    cam, class_idx, confidence = gradcam.generate_heatmap(img_tensor)
    gradcam.remove_hooks()

    display_img = get_raw_display_transforms()(image)
    overlay = overlay_heatmap(display_img, cam, alpha=0.55)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(out_file)

    predicted_food = predictor.classes[class_idx]
    print(f"\nGrad-CAM generation successful:")
    print(f"- Predicted class: {predicted_food} ({confidence*100:.1f}%)")
    print(f"- Target layer: {target_layer}")
    print(f"- Saliency heatmap saved to: {out_file.resolve()}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Grad-CAM visualization for local image")
    parser.add_argument("image", help="Path to input image file")
    parser.add_argument("--output", default="results/plots/gradcam_output.jpg")
    parser.add_argument("--model", default="mobilenet_v3_large")
    parser.add_argument("--weights", default=None)
    args = parser.parse_args()

    generate_local_gradcam(
        image_path=args.image,
        output_path=args.output,
        model_name=args.model,
        weights_path=args.weights
    )
