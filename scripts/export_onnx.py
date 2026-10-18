"""
CLI tool to export StreetFoodAI PyTorch models to ONNX.
"""
import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.inference.onnx_export import export_to_onnx

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export model to ONNX")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0"])
    parser.add_argument("--weights", default=None)
    parser.add_argument("--output", default="models/checkpoints/streetfood_model.onnx")
    args = parser.parse_args()

    export_to_onnx(
        model_name=args.model,
        weights_path=args.weights,
        output_path=args.output
    )
