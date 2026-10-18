"""
EfficientNet-B0 Architecture for Indian Street Food Recognition.
Balancing feature representation accuracy and model efficiency with compound scaling.
"""
from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class StreetFoodEfficientNetB0(nn.Module):
    def __init__(
        self,
        num_classes: int = 20,
        pretrained: bool = True,
        dropout: float = 0.2,
        freeze_backbone: bool = False
    ):
        super().__init__()
        weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.base_model = efficientnet_b0(weights=weights)

        # Freeze feature backbone if requested
        if freeze_backbone:
            for param in self.base_model.features.parameters():
                param.requires_grad = False

        # Replace classification head
        # In torchvision efficientnet_b0:
        # classifier is:
        # (0): Dropout(p=0.2, inplace=True)
        # (1): Linear(in_features=1280, out_features=1000, bias=True)
        in_features = self.base_model.classifier[1].in_features
        self.base_model.classifier[0] = nn.Dropout(p=dropout)
        self.base_model.classifier[1] = nn.Linear(in_features, num_classes)

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

def build_efficientnet_b0(
    num_classes: int = 20,
    pretrained: bool = True,
    dropout: float = 0.2,
    freeze_backbone: bool = False
) -> StreetFoodEfficientNetB0:
    return StreetFoodEfficientNetB0(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout=dropout,
        freeze_backbone=freeze_backbone
    )
