from typing import Optional
from pydantic import BaseModel, ConfigDict

class HistoryCreate(BaseModel):
    food_name: str
    confidence: float
    serving_size: str = "Regular"
    serving_weight_g: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    is_uncertain: bool = False
    model_architecture: Optional[str] = "mobilenet_v3_large"
    notes: Optional[str] = None

class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: Optional[str] = None
    food_name: str
    confidence: float
    serving_size: str
    serving_weight_g: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    is_uncertain: bool
    model_architecture: Optional[str] = None
    notes: Optional[str] = None
