"""
Dataset Preparation & Cleaning Pipeline for StreetFoodAI.
Handles:
- Image format validation & corruption removal
- Exact duplicate detection via cryptographic hashing (prevents data leakage across splits)
- Stratified train/val/test splitting
- Imbalance detection and dataset quality reporting
"""
import os
import shutil
import hashlib
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from PIL import Image
import numpy as np

def compute_image_hash(filepath: Path) -> str:
    """Computes SHA-256 hash of image file contents to identify exact duplicates."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_valid_image(filepath: Path, min_dimension: int = 50) -> Tuple[bool, str]:
    """Validates that image is uncorrupted, readable, and meets minimum dimension requirements."""
    try:
        with Image.open(filepath) as img:
            img.verify() # Verify file header integrity
        # Re-open to check dimensions and decode capability
        with Image.open(filepath) as img:
            w, h = img.size
            if w < min_dimension or h < min_dimension:
                return False, f"Image dimensions too small ({w}x{h} < {min_dimension})"
            # Ensure it can convert to RGB
            _ = img.convert("RGB")
        return True, "Valid"
    except Exception as e:
        return False, str(e)

def sanitize_folder_name(name: str) -> str:
    r"""Replaces invalid Windows path characters like / or \ with underscores."""
    return name.replace("/", "_").replace("\\", "_")

def prepare_and_split_dataset(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed",
    metadata_dir: str = "data/metadata",
    classes_config: str = "ml/config/classes.json",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42
) -> Dict:
    """
    Scans raw directory, removes duplicates and corrupted files,
    performs stratified split, and writes metadata summaries.
    """
    raw_path = Path(raw_dir)
    processed_path = Path(processed_dir)
    metadata_path = Path(metadata_dir)
    metadata_path.mkdir(parents=True, exist_ok=True)

    with open(classes_config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    classes = cfg["classes"]

    np.random.seed(random_seed)

    report = {
        "raw_images_found": 0,
        "valid_images": 0,
        "corrupted_images": [],
        "duplicate_images": [],
        "splits": {"train": 0, "val": 0, "test": 0},
        "class_distribution": {},
        "imbalance_ratio": 1.0,
        "severe_imbalance_warning": False,
        "random_seed": random_seed
    }

    seen_hashes: Dict[str, Path] = {}
    valid_class_files: Dict[str, List[Path]] = {cls_name: [] for cls_name in classes}

    # 1. Scan raw_path
    if not raw_path.exists():
        raw_path.mkdir(parents=True, exist_ok=True)
        # Create class subfolders for convenience
        for cls_name in classes:
            (raw_path / sanitize_folder_name(cls_name)).mkdir(exist_ok=True)
        print(f"Created empty raw directory structure at {raw_path}. Place category images there.")
        return report

    print(f"Scanning raw images in {raw_path}...")
    for cls_name in classes:
        # Check standard name, sanitized name, or slugified name
        class_folder = raw_path / cls_name
        if not class_folder.is_dir():
            class_folder = raw_path / sanitize_folder_name(cls_name)
        if not class_folder.is_dir():
            slug = cls_name.lower().replace(" ", "_").replace("/", "_")
            class_folder = raw_path / slug

        if not class_folder.is_dir():
            continue

        for file_path in class_folder.iterdir():
            if file_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
                continue

            report["raw_images_found"] += 1
            # Check validity
            is_valid, reason = is_valid_image(file_path)
            if not is_valid:
                report["corrupted_images"].append({"file": str(file_path), "reason": reason})
                continue

            # Check duplicate hash
            file_hash = compute_image_hash(file_path)
            if file_hash in seen_hashes:
                report["duplicate_images"].append({
                    "file": str(file_path),
                    "duplicate_of": str(seen_hashes[file_hash])
                })
                continue

            seen_hashes[file_hash] = file_path
            valid_class_files[cls_name].append(file_path)
            report["valid_images"] += 1

    # 2. Check class distributions and imbalance
    counts = [len(files) for files in valid_class_files.values()]
    for cls_name, files in valid_class_files.items():
        report["class_distribution"][cls_name] = len(files)

    non_zero_counts = [c for c in counts if c > 0]
    if non_zero_counts:
        max_c = max(non_zero_counts)
        min_c = min(non_zero_counts)
        imbalance = max_c / min_c if min_c > 0 else 1.0
        report["imbalance_ratio"] = round(imbalance, 2)
        if imbalance > 3.0:
            report["severe_imbalance_warning"] = True

    # 3. Stratified Split and Copy to data/processed
    train_dir = processed_path / "train"
    val_dir = processed_path / "val"
    test_dir = processed_path / "test"

    for d in [train_dir, val_dir, test_dir]:
        d.mkdir(parents=True, exist_ok=True)
        for cls_name in classes:
            (d / sanitize_folder_name(cls_name)).mkdir(parents=True, exist_ok=True)

    for cls_name, files in valid_class_files.items():
        if not files:
            continue
        # Shuffle deterministically
        indices = np.random.permutation(len(files))
        n_total = len(files)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        # Ensure at least 1 image in train if only 1 image exists
        if n_train == 0 and n_total > 0:
            n_train = 1

        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]

        folder_name = sanitize_folder_name(cls_name)
        for idx in train_idx:
            src = files[idx]
            dst = train_dir / folder_name / src.name
            shutil.copy2(src, dst)
            report["splits"]["train"] += 1

        for idx in val_idx:
            src = files[idx]
            dst = val_dir / folder_name / src.name
            shutil.copy2(src, dst)
            report["splits"]["val"] += 1

        for idx in test_idx:
            src = files[idx]
            dst = test_dir / folder_name / src.name
            shutil.copy2(src, dst)
            report["splits"]["test"] += 1

    # Save summary report
    summary_path = metadata_path / "dataset_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Dataset preparation complete:")
    print(f"- Raw images scanned: {report['raw_images_found']}")
    print(f"- Valid unique images: {report['valid_images']}")
    print(f"- Duplicates detected: {len(report['duplicate_images'])}")
    print(f"- Corrupted images removed: {len(report['corrupted_images'])}")
    print(f"- Split: Train={report['splits']['train']}, Val={report['splits']['val']}, Test={report['splits']['test']}")
    print(f"- Summary saved to: {summary_path}")

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Dataset Preparation")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw image directory")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to output processed directory")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train split ratio (default: 0.70)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation split ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test split ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    prepare_and_split_dataset(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_seed=args.seed
    )
