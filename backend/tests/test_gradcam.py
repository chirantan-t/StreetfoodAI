"""
Tests for Grad-CAM Explainability Module.
Verifies convolutional feature hook registration, heatmap normalization, and overlay synthesis.
"""
from PIL import Image
import numpy as np
import torch
from ml.models.mobilenet import build_mobilenet_v3_large
from ml.explainability.gradcam import GradCAM, overlay_heatmap, image_to_base64

def test_gradcam_generation_and_hooks():
    model = build_mobilenet_v3_large(num_classes=20, pretrained=False)
    target_layer = model.get_target_layer_for_gradcam()
    gradcam = GradCAM(model=model, target_layer=target_layer)

    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=True)
    cam, class_idx, confidence = gradcam.generate_heatmap(dummy_input, target_class_idx=0)
    gradcam.remove_hooks()

    assert cam is not None
    assert isinstance(cam, np.ndarray)
    assert cam.ndim == 2
    # Verify normalized in range [0, 1]
    assert np.min(cam) >= 0.0
    assert np.max(cam) <= 1.0
    assert 0 <= class_idx < 20
    assert 0.0 <= confidence <= 1.0

def test_gradcam_overlay_dimensions():
    original_img = Image.new("RGB", (250, 180), color="yellow")
    cam = np.random.uniform(0.0, 1.0, size=(14, 14)).astype(np.float32)

    overlay = overlay_heatmap(original_img, cam, alpha=0.5)

    assert overlay is not None
    # Verifies original dimensions are preserved
    assert overlay.size == original_img.size
    assert overlay.mode == "RGB"

    base64_str = image_to_base64(overlay)
    assert base64_str.startswith("data:image/jpeg;base64,")
