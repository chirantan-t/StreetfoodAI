from typing import Optional, Dict, Any
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    model_architecture: str
    model_weights_status: str
    device: str
    is_model_ready: bool
    num_classes: int
    supported_classes: list[str]
