"""
Dataset Quality Validation and Class Distribution Reporting Tool for StreetFoodAI.
Can be run on either raw/ or processed/ directories.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict
from PIL import Image
import matplotlib.pyplot as plt

def validate_dataset_quality(data_dir: str = "data/processed/train", output_plot: str = "results/plots/class_distribution.png") -> Dict:
    path = Path(data_dir)
    print(f"Validating dataset quality at: {path.resolve()}")

    if not path.exists():
        print(f"Directory {data_dir} does not exist yet.")
        return {"status": "missing_directory", "path": str(path)}

    classes = [d.name for d in path.iterdir() if d.is_dir()]
    class_counts = {}
    corrupted_files = []
    total_images = 0

    for cls in sorted(classes):
        cls_folder = path / cls
        count = 0
        for f in cls_folder.iterdir():
            if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                try:
                    with Image.open(f) as img:
                        img.verify()
                    count += 1
                except Exception as e:
                    corrupted_files.append((str(f), str(e)))
        class_counts[cls] = count
        total_images += count

    print(f"\nTotal Valid Images Found: {total_images}")
    print(f"Total Corrupted Files: {len(corrupted_files)}")
    print("\nClass Breakdown:")
    for cls, count in class_counts.items():
        print(f"  - {cls:<25}: {count} images")

    # Imbalance analysis
    non_zero = [c for c in class_counts.values() if c > 0]
    imbalance_ratio = 1.0
    if non_zero:
        imbalance_ratio = max(non_zero) / min(non_zero)
        print(f"\nImbalance Ratio (Max / Min): {imbalance_ratio:.2f}")
        if imbalance_ratio > 3.0:
            print("WARNING: Severe class imbalance detected! Consider class-weighted loss or data augmentation.")

    # Generate plot if any images exist
    if total_images > 0:
        os.makedirs(Path(output_plot).parent, exist_ok=True)
        plt.figure(figsize=(12, 6))
        sorted_items = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        labels = [x[0] for x in sorted_items]
        values = [x[1] for x in sorted_items]

        plt.bar(range(len(labels)), values, color="#f97316", edgecolor="#c2410c", alpha=0.85)
        plt.xticks(range(len(labels)), labels, rotation=45, ha="right", fontsize=9)
        plt.title(f"StreetFoodAI Class Distribution ({path.name} set)", fontsize=14, fontweight="bold", pad=15)
        plt.ylabel("Number of Images", fontsize=11)
        plt.tight_layout()
        plt.savefig(output_plot, dpi=300)
        plt.close()
        print(f"Class distribution chart saved to: {output_plot}")

    return {
        "data_dir": str(path),
        "total_images": total_images,
        "corrupted_count": len(corrupted_files),
        "imbalance_ratio": round(imbalance_ratio, 2),
        "class_counts": class_counts
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset Quality Validator")
    parser.add_argument("--data-dir", default="data/processed/train", help="Dataset split directory to validate")
    parser.add_argument("--plot-path", default="results/plots/class_distribution.png", help="Path to save class distribution plot")
    args = parser.parse_args()

    validate_dataset_quality(args.data_dir, args.plot_path)
