"""
Tests for Inference Engine, Entropy Scoring, and Unknown Food Out-of-Distribution Handling.
"""
from PIL import Image
import pytest
from ml.inference.predictor import StreetFoodPredictor

@pytest.fixture
def predictor():
    return StreetFoodPredictor(
        model_name="mobilenet_v3_large",
        weights_path=None,  # un-fine-tuned weights
        confidence_threshold=0.60
    )

def test_predictor_missing_model_weights_status(predictor):
    """
    Verifies that when custom weights are absent, the system explicitly reports
    'backbone_pretrained_head_untrained' rather than inventing false confidence or pretending fine-tuning.
    """
    assert predictor.model is not None
    assert predictor.metadata["weights_loaded"] is False
    assert predictor.metadata["status"] == "backbone_pretrained_head_untrained"

def test_prediction_output_structure(predictor):
    """Verifies complete response structure for a synthetic image."""
    img = Image.new("RGB", (224, 224), color="orange")
    result = predictor.predict(img, top_k=5)

    assert "predicted_food" in result
    assert "confidence" in result
    assert "entropy" in result
    assert "is_uncertain" in result
    assert "top_candidates" in result
    assert len(result["top_candidates"]) == 5

def test_unknown_food_threshold_rejection():
    """
    Verifies that when confidence is forced below the threshold,
    the framework flags uncertainty and labels as 'Other / Unknown Food'.
    """
    strict_predictor = StreetFoodPredictor(
        model_name="mobilenet_v3_large",
        confidence_threshold=0.99  # very strict threshold
    )
    img = Image.new("RGB", (224, 224), color="gray")
    result = strict_predictor.predict(img)

    assert result["is_uncertain"] is True
    assert result["predicted_food"] == "Other / Unknown Food"
    assert "below decision threshold" in result["rejection_reason"]
