"""
Production Inference Engine for StreetFoodAI.
Features:
- Singleton model caching
- Preprocessing matching training resolution (224x224)
- Top-K probability extraction
- Out-of-distribution and unknown-food detection thresholding
- Integration with nutritional lookup
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.data.augmentation import get_eval_transforms
from ml.models.registry import get_model, load_classes_config

class StreetFoodPredictor:
    def __init__(
        self,
        model_name: str = "mobilenet_v3_large",
        weights_path: Optional[str] = None,
        classes_config_path: str = "ml/config/classes.json",
        confidence_threshold: float = 0.25,
        entropy_threshold: float = 2.40,
        auto_load_checkpoint: bool = False,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.weights_path = weights_path
        self.classes_config_path = classes_config_path
        self.confidence_threshold = confidence_threshold
        self.entropy_threshold = entropy_threshold
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Auto-discover fine-tuned weights only if requested
        if auto_load_checkpoint and self.weights_path is None:
            candidates = [
                Path(f"ml/checkpoints/best_{self.model_name}.pth"),
                Path(f"ml/checkpoints/{self.model_name}_best.pth")
            ]
            for candidate in candidates:
                if candidate.exists():
                    self.weights_path = str(candidate)
                    break

        # Load class configuration
        self.classes_cfg = load_classes_config(classes_config_path)
        self.classes = self.classes_cfg["classes"]
        self.num_classes = len(self.classes)
        self.unknown_idx = self.classes_cfg.get("unknown_class_id", 19)

        self.transform = get_eval_transforms(image_size=224)
        self.model = None
        self.metadata = {}
        self._weights_mtime = None
        self._load_model()

    def _load_model(self):
        if self.weights_path and os.path.exists(self.weights_path):
            try:
                self._weights_mtime = os.path.getmtime(self.weights_path)
            except Exception:
                self._weights_mtime = None

        print(f"Initializing StreetFoodPredictor with architecture={self.model_name} on device={self.device}")
        self.model, self.metadata = get_model(
            arch_name=self.model_name,
            num_classes=self.num_classes,
            weights_path=self.weights_path,
            pretrained=True,
            device=self.device
        )
        self.model.eval()

    def check_and_reload_weights(self):
        """Checks if underlying checkpoint weights have been updated on disk and hot-reloads them."""
        if self.weights_path and os.path.exists(self.weights_path):
            try:
                current_mtime = os.path.getmtime(self.weights_path)
                if self._weights_mtime is not None and current_mtime > self._weights_mtime:
                    print(f"Detected updated weights at {self.weights_path} (mtime {current_mtime} > {self._weights_mtime}). Hot-reloading...")
                    self._load_model()
            except Exception as e:
                print(f"Warning: Failed to check/reload weights: {e}")

    def predict(
        self,
        image: Image.Image,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Runs inference on a PIL Image.
        Applies softmax, measures prediction entropy, checks confidence thresholds,
        and provides candidates.
        """
        self.check_and_reload_weights()
        img_rgb = image.convert("RGB")
        img_tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(img_tensor)
            probs = F.softmax(logits, dim=-1).squeeze(0) # [num_classes]

        probs_np = probs.cpu().numpy()

        # Compute Shannon Entropy in nats: H(p) = -sum(p * log(p))
        # High entropy indicates uniform/flat distribution (high uncertainty)
        eps = 1e-9
        entropy = float(-np.sum(probs_np * np.log(probs_np + eps)))

        # Top-K predictions
        top_indices = np.argsort(probs_np)[::-1][:top_k]
        top_candidates = []
        for idx in top_indices:
            top_candidates.append({
                "class_index": int(idx),
                "food_name": self.classes[idx],
                "confidence": round(float(probs_np[idx]), 4)
            })

        best_idx = int(top_indices[0])
        best_class = self.classes[best_idx]
        best_confidence = float(probs_np[best_idx])

        # Unknown / Out-of-Distribution Rejection Logic:
        # 1. If best confidence is below configured threshold
        # 2. Or entropy exceeds the threshold (flat prediction)
        # 3. Or best class is explicitly classified into 'Other / Unknown Food'
        is_uncertain = False
        rejection_reason = None

        if best_confidence < self.confidence_threshold:
            is_uncertain = True
            rejection_reason = (
                f"Confidence {best_confidence:.1%} is below decision threshold "
                f"({self.confidence_threshold:.1%}). Model is uncertain."
            )
        elif entropy > self.entropy_threshold:
            is_uncertain = True
            rejection_reason = (
                f"Prediction entropy ({entropy:.2f}) indicates high ambiguity across multiple classes."
            )
        elif best_idx == self.unknown_idx:
            is_uncertain = True
            rejection_reason = "Identified as outside standard Indian street food category index."

        return {
            "predicted_food": best_class if not is_uncertain else "Other / Unknown Food",
            "predicted_class_index": best_idx,
            "raw_top_class": best_class,
            "confidence": round(best_confidence, 4),
            "entropy": round(entropy, 4),
            "is_uncertain": is_uncertain,
            "rejection_reason": rejection_reason,
            "top_candidates": top_candidates,
            "model_architecture": self.model_name,
            "weights_status": self.metadata.get("status", "unknown")
        }

    def get_model_for_gradcam(self) -> Tuple[torch.nn.Module, torch.nn.Module]:
        """Returns model and its target convolutional layer for Grad-CAM."""
        if hasattr(self.model, "get_target_layer_for_gradcam"):
            target_layer = self.model.get_target_layer_for_gradcam()
            return self.model, target_layer
        elif hasattr(self.model, "features"):
            return self.model, self.model.features[-1]
        else:
            raise NotImplementedError(f"Grad-CAM layer discovery not supported for {self.model_name}")
