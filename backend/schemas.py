"""Pydantic schemas shared across endpoints."""

from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: str = ""
    language: str = "en"  # User's selected language code (en, hi, mr, ta, te, kn, ml, gu, bn, pa)


class WeatherRequest(BaseModel):
    lat: float
    lon: float
    include_ai: bool = True


class CropPlanRequest(BaseModel):
    userId: str
    cropName: str
    location: str
    soilType: str
    sowingDate: str
    irrigationMethod: str
    landSizeAcres: float
    expectedInvestment: Optional[float] = None
    waterSourceType: Optional[str] = None
