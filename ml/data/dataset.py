"""
StreetFoodDataset: PyTorch Dataset for Indian street food classification.
Supports directory hierarchies, label mapping, and robust PIL image validation.
"""
import os
import json
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Dict
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import torch
from torch.utils.data import Dataset

class StreetFoodDataset(Dataset):
    """
    Standard PyTorch Dataset for loading Indian Street Food images organized by class directories.
    Directory structure expected:
      root_dir/
         Vada Pav/
            img1.jpg
         Pav Bhaji/
            img2.jpg
    """
    def __init__(
        self,
        root_dir: str,
        transform: Optional[Callable] = None,
        classes_config_path: Optional[str] = None,
        allowed_extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")
    ):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.allowed_extensions = allowed_extensions

        # Load class mappings
        if classes_config_path and os.path.exists(classes_config_path):
            with open(classes_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.classes = config["classes"]
                self.class_to_idx = config["class_to_id"]
                self.idx_to_class = {int(k): v for k, v in config["id_to_class"].items()}
        else:
            # Fallback to subdirectory names sorted alphabetically
            if self.root_dir.exists():
                subdirs = sorted([d.name for d in self.root_dir.iterdir() if d.is_dir()])
                self.classes = subdirs
                self.class_to_idx = {cls_name: i for i, cls_name in enumerate(subdirs)}
                self.idx_to_class = {i: cls_name for i, cls_name in enumerate(subdirs)}
            else:
                self.classes = []
                self.class_to_idx = {}
                self.idx_to_class = {}

        self.samples: List[Tuple[Path, int]] = []
        self._load_samples()

    def _load_samples(self):
        """Discovers valid image files and maps to class indices."""
        if not self.root_dir.exists():
            return

        for class_name, idx in self.class_to_idx.items():
            class_folder = self.root_dir / class_name
            if not class_folder.is_dir():
                sanitized = class_name.replace("/", "_").replace("\\", "_")
                class_folder = self.root_dir / sanitized
                if not class_folder.is_dir():
                    slug = class_name.lower().replace(" ", "_").replace("/", "_")
                    class_folder = self.root_dir / slug
                    if not class_folder.is_dir():
                        continue

            for file_path in class_folder.iterdir():
                if file_path.suffix.lower() in self.allowed_extensions:
                    self.samples.append((file_path, idx))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        img_path, label = self.samples[idx]
        try:
            with Image.open(img_path) as img:
                image = img.convert("RGB")
        except Exception as e:
            # If an image is unreadable at runtime, log and return a black tensor fallback
            print(f"Warning: Corrupted image at {img_path}: {e}")
            image = Image.new("RGB", (224, 224), (0, 0, 0))

        if self.transform:
            try:
                image = self.transform(image)
            except Exception as e:
                # Fallback to neutral black tensor if augmentation encounters an invalid image
                black = Image.new("RGB", (224, 224), (0, 0, 0))
                from ml.data.augmentation import get_eval_transforms
                image = get_eval_transforms()(black)

        return image, label, str(img_path)

    def get_class_counts(self) -> Dict[str, int]:
        """Returns sample count for each food class in the dataset."""
        counts = {cls_name: 0 for cls_name in self.classes}
        for _, label_idx in self.samples:
            cls_name = self.idx_to_class.get(label_idx, "Unknown")
            counts[cls_name] = counts.get(cls_name, 0) + 1
        return counts
