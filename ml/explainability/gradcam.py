"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for StreetFoodAI.
Provides visual explanations of convolutional network decisions for Indian street food.
Applies pure PyTorch hook mechanism with OpenCV JET colormap blending.
"""
from typing import Tuple, Optional, Union
import io
import base64
import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F

class GradCAM:
    """
    Hook-based Grad-CAM implementation for CNN feature maps.
    Computes importance weights alpha_k = (1/Z) * sum_i sum_j (d y^c / d A^k_ij)
    and generates localized attention map L^c = ReLU(sum_k alpha_k * A^k).
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None
        self._handlers = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        h1 = self.target_layer.register_forward_hook(forward_hook)
        h2 = self.target_layer.register_full_backward_hook(backward_hook)
        self._handlers.extend([h1, h2])

    def remove_hooks(self):
        for h in self._handlers:
            h.remove()
        self._handlers = []

    def generate_heatmap(
        self,
        input_tensor: torch.Tensor,
        target_class_idx: Optional[int] = None
    ) -> Tuple[np.ndarray, int, float]:
        """
        Generates raw Grad-CAM heatmap array [H, W] normalized in [0, 1].
        """
        self.model.eval()
        self.model.zero_grad()

        # Forward pass
        logits = self.model(input_tensor)
        probabilities = F.softmax(logits, dim=-1)

        if target_class_idx is None:
            target_class_idx = int(torch.argmax(logits, dim=-1).item())

        confidence = float(probabilities[0, target_class_idx].item())

        # Target score for backprop
        score = logits[0, target_class_idx]
        score.backward()

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Gradients or activations were not captured. Verify target_layer.")

        # Global average pooling of gradients
        # activations: [1, C, H, W], gradients: [1, C, H, W]
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True) # [1, C, 1, 1]
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True) # [1, 1, H, W]

        # Apply ReLU to retain only features that positively correlate with the class
        cam = F.relu(cam)

        cam = cam.squeeze().cpu().numpy()
        # Normalize to [0, 1]
        cam_min, cam_max = np.min(cam), np.max(cam)
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam, target_class_idx, confidence

def overlay_heatmap(
    original_image: Image.Image,
    cam: np.ndarray,
    alpha: float = 0.5,
    colormap: int = cv2.COLORMAP_JET
) -> Image.Image:
    """
    Overlays 2D CAM heatmap [H, W] on top of original PIL image.
    """
    img_rgb = np.array(original_image.convert("RGB"))
    h, w, _ = img_rgb.shape

    # Resize CAM to match original image dimensions
    cam_resized = cv2.resize(cam, (w, h), interpolation=cv2.INTER_LINEAR)
    cam_uint8 = np.uint8(255 * cam_resized)

    # Apply colormap (OpenCV returns BGR)
    heatmap_bgr = cv2.applyColorMap(cam_uint8, colormap)
    heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)

    # Blend original image and heatmap
    blended = np.uint8(alpha * heatmap_rgb + (1.0 - alpha) * img_rgb)
    return Image.fromarray(blended)

def image_to_base64(pil_img: Image.Image, format: str = "JPEG") -> str:
    """Encodes PIL image to Base64 data URL string."""
    buffer = io.BytesIO()
    pil_img.save(buffer, format=format)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded}"
