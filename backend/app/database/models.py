"""
Database models for prediction history and nutritional logs.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PredictionRecord(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    food_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    serving_size = Column(String(50), default="Regular", nullable=False)
    serving_weight_g = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    is_uncertain = Column(Boolean, default=False)
    model_architecture = Column(String(50), default="mobilenet_v3_large")
    notes = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "food_name": self.food_name,
            "confidence": self.confidence,
            "serving_size": self.serving_size,
            "serving_weight_g": self.serving_weight_g,
            "calories": self.calories,
            "protein": self.protein,
            "carbohydrates": self.carbohydrates,
            "fat": self.fat,
            "fiber": self.fiber,
            "is_uncertain": self.is_uncertain,
            "model_architecture": self.model_architecture,
            "notes": self.notes
        }
