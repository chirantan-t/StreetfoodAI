"""
Script to evaluate trained StreetFoodAI models on test dataset splits.
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.evaluation.evaluate import evaluate_model
from ml.evaluation.compare import generate_model_comparison
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Model Evaluation CLI")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0", "all"])
    parser.add_argument("--weights", default=None, help="Path to checkpoint weights")
    parser.add_argument("--test-dir", default="data/processed/test")
    parser.add_argument("--compare", action="store_true", help="Generate cross-model comparison report")
    args = parser.parse_args()

    if args.model == "all" or args.compare:
        generate_model_comparison()
    else:
        evaluate_model(
            model_name=args.model,
            weights_path=args.weights,
            test_dir=args.test_dir
        )
