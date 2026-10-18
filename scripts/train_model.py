"""
Script to train or fine-tune StreetFoodAI models (MobileNetV3-Large or EfficientNet-B0).
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.training.train import run_training
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Model Training CLI")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0"])
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--optimizer", default="adamw", choices=["adamw", "sgd"])
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--no-mlflow", action="store_true")
    args = parser.parse_args()

    run_training(
        model_name=args.model,
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        optimizer_type=args.optimizer,
        patience=args.patience,
        resume_checkpoint=args.resume,
        use_mlflow=not args.no_mlflow
    )
