from typing import Optional
from pydantic import BaseModel

class ExplainResponse(BaseModel):
    predicted_class: str
    target_class_index: int
    confidence: float
    heatmap_overlay_base64: str
    target_layer: str
    explanation_method: str = "Grad-CAM"
    disclaimer: str = (
        "Grad-CAM visualizes gradient attention maps of the final convolutional layer. "
        "It illustrates which image regions contributed most to the model's activation score, "
        "and is intended as an explanatory aid rather than proof of classification accuracy."
    )
