from typing import Optional
from pydantic import BaseModel

class NutritionData(BaseModel):
    food_id: Optional[str] = None
    food_name: str
    category: Optional[str] = "Street Food"
    serving_size: str = "Regular"
    serving_description: Optional[str] = None
    serving_weight_g: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    data_source: Optional[str] = "IFCT 2017 (ICMR-NIN)"
    source_reference: Optional[str] = None
    notes_uncertainty: Optional[str] = None
    disclaimer: Optional[str] = None
    is_available: bool = True
