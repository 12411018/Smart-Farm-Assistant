"""Pydantic schemas shared across endpoints."""

from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: str = ""


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
