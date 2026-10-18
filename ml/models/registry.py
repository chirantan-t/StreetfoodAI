"""
Model Registry and Factory for StreetFoodAI.
Unified access point for MobileNetV3-Large, EfficientNet-B0, and CLIP zero-shot.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import torch
import torch.nn as nn

from ml.models.mobilenet import build_mobilenet_v3_large
from ml.models.efficientnet import build_efficientnet_b0
from ml.models.clip_classifier import StreetFoodCLIPClassifier

SUPPORTED_ARCHITECTURES = ["mobilenet_v3_large", "efficientnet_b0", "clip"]

def load_classes_config(config_path: str = "ml/config/classes.json") -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_model(
    arch_name: str = "mobilenet_v3_large",
    num_classes: int = 20,
    weights_path: Optional[str] = None,
    pretrained: bool = True,
    freeze_backbone: bool = False,
    device: str = "cpu"
) -> Tuple[nn.Module, Dict[str, Any]]:
    """
    Builds and returns model instance and metadata status.
    Metadata explicitly indicates whether custom weights were loaded or
    if only pretrained backbone weights are active.
    """
    arch_name = arch_name.lower()
    if arch_name not in SUPPORTED_ARCHITECTURES:
        raise ValueError(f"Unsupported architecture '{arch_name}'. Choose from {SUPPORTED_ARCHITECTURES}")

    metadata = {
        "architecture": arch_name,
        "num_classes": num_classes,
        "device": device,
        "weights_loaded": False,
        "weights_path": weights_path,
        "status": "initial"
    }

    has_custom_weights = weights_path and os.path.exists(weights_path)
    use_pretrained = pretrained and not has_custom_weights

    if arch_name == "mobilenet_v3_large":
        model = build_mobilenet_v3_large(num_classes=num_classes, pretrained=use_pretrained, freeze_backbone=freeze_backbone)
    elif arch_name == "efficientnet_b0":
        model = build_efficientnet_b0(num_classes=num_classes, pretrained=use_pretrained, freeze_backbone=freeze_backbone)
    elif arch_name == "clip":
        classes_cfg = load_classes_config()
        clip_model = StreetFoodCLIPClassifier(classes=classes_cfg["classes"], device=device)
        return clip_model, {"architecture": "clip", "status": "clip_ready", "device": device}

    # Load custom weights if provided and exists
    if weights_path and os.path.exists(weights_path):
        try:
            checkpoint = torch.load(weights_path, map_location=device)
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                model.load_state_dict(checkpoint["state_dict"])
                metadata["epoch"] = checkpoint.get("epoch", None)
                metadata["val_accuracy"] = checkpoint.get("val_accuracy", None)
            elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            else:
                model.load_state_dict(checkpoint)
            metadata["weights_loaded"] = True
            metadata["status"] = "fine_tuned_weights_loaded"
            print(f"Successfully loaded model weights from {weights_path}")
        except Exception as e:
            metadata["status"] = f"weights_load_error: {str(e)}"
            print(f"Warning: Failed loading weights from {weights_path}: {e}")
    else:
        if pretrained:
            metadata["status"] = "backbone_pretrained_head_untrained"
        else:
            metadata["status"] = "random_initialization"

    model.to(device)
    model.eval()
    return model, metadata
