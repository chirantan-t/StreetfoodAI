"""
MobileNetV3-Large Architecture for Indian Street Food Recognition.
Configured for efficient, low-latency mobile and edge inference.
"""
from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights

class StreetFoodMobileNetV3(nn.Module):
    def __init__(
        self,
        num_classes: int = 20,
        pretrained: bool = True,
        dropout: float = 0.2,
        freeze_backbone: bool = False
    ):
        super().__init__()
        weights = MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        self.base_model = mobilenet_v3_large(weights=weights)

        # Freeze feature backbone if requested
        if freeze_backbone:
            for param in self.base_model.features.parameters():
                param.requires_grad = False

        # Replace classification head
        # In torchvision mobilenet_v3_large:
        # classifier is:
        # (0): Linear(960, 1280)
        # (1): Hardswish()
        # (2): Dropout(p=0.2, inplace=True)
        # (3): Linear(1280, 1000)
        in_features = self.base_model.classifier[0].out_features  # 1280
        self.base_model.classifier[2] = nn.Dropout(p=dropout)
        self.base_model.classifier[3] = nn.Linear(in_features, num_classes)

        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base_model(x)

    def get_target_layer_for_gradcam(self) -> nn.Module:
        """Returns the final convolutional block in features."""
        return self.base_model.features[-1]

    def unfreeze_backbone(self):
        """Unfreezes all parameters for full fine-tuning."""
        for param in self.parameters():
            param.requires_grad = True

def build_mobilenet_v3_large(
    num_classes: int = 20,
    pretrained: bool = True,
    dropout: float = 0.2,
    freeze_backbone: bool = False
) -> StreetFoodMobileNetV3:
    return StreetFoodMobileNetV3(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout=dropout,
        freeze_backbone=freeze_backbone
    )
