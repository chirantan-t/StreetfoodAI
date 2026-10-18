#!/usr/bin/env python3
"""Compute CLIP image embeddings for downloaded dataset images."""
import os
import csv, json
from pathlib import Path
import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "data" / "images"
OUT = ROOT / "data" / "embeddings"
CACHE_DIR = ROOT / "data" / "cache"
OUT.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

os.environ["HF_HOME"] = str(CACHE_DIR / "huggingface")
os.environ["TORCH_HOME"] = str(CACHE_DIR / "torch")

import open_clip

MODEL_NAME = "ViT-B-32"
PRETRAINED = "laion2b_s34b_b79k"

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED,
        cache_dir=str(CACHE_DIR / "open_clip")
    )
    model = model.to(device).eval()
    image_paths = sorted(p for p in IMAGE_ROOT.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    if not image_paths:
        raise SystemExit("No images found. Run scripts/download_commons_dataset.py first.")
    vectors, rows = [], []
    with torch.no_grad():
        for idx, path in enumerate(image_paths, start=1):
            try:
                image = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
                feat = model.encode_image(image)
                feat = feat / feat.norm(dim=-1, keepdim=True)
                vectors.append(feat.cpu().numpy()[0].astype(np.float32))
                rows.append({
                    "embedding_index": idx - 1,
                    "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "class_folder": path.parent.name,
                    "filename": path.name,
                    "model_name": MODEL_NAME,
                    "pretrained_weights": PRETRAINED
                })
                if idx % 25 == 0:
                    print(f"Embedded {idx}/{len(image_paths)} images")
            except Exception as e:
                print(f"Skipping {path}: {e}")
    if not vectors:
        raise SystemExit("Could not embed any images.")
    np.save(OUT / "embeddings.npy", np.stack(vectors))
    with (OUT / "embedding_index.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT / "embedding_config.json").write_text(json.dumps({
        "model_name": MODEL_NAME,
        "pretrained_weights": PRETRAINED,
        "embedding_dimension": int(vectors[0].shape[0]),
        "normalization": "L2-normalized",
        "count": len(vectors),
        "device": device
    }, indent=2), encoding="utf-8")
    print(f"Saved {len(vectors)} embeddings to {OUT}")
if __name__ == "__main__":
    main()
