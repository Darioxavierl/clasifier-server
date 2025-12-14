# app/schemas/prediction.py
from pydantic import BaseModel
from typing import Optional

class AlternativeClass(BaseModel):
    class_name: str
    confidence: float

class PredictionResponse(BaseModel):
    """Respuesta completa para frontend/debugging"""
    code: int
    class_name: str
    confidence: float
    is_confident: bool
    description: str
    alternative_classes: list[AlternativeClass]
    requires_review: Optional[bool] = False
    review_reason: Optional[str] = None
    special_handling: Optional[bool] = False
    handling_notes: Optional[str] = None

class ESPResponse(BaseModel):
    """Respuesta minimalista para ESP32"""
    code: int