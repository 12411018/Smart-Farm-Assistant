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


class IrrigationStatusEvent(BaseModel):
    event: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    water_liters: Optional[float] = None
    rain: Optional[float] = None
    soil: Optional[float] = None


class IrrigationStatusPayload(BaseModel):
    start: Optional[IrrigationStatusEvent] = None
    end: Optional[IrrigationStatusEvent] = None
