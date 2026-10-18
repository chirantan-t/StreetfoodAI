"""
Script to prepare, validate, clean, deduplicate, and split the Indian Street Food dataset.
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.data.prep_dataset import prepare_and_split_dataset
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Dataset Preparation CLI")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw image folder")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to processed output")
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    prepare_and_split_dataset(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_seed=args.seed
    )
