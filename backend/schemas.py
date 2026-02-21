"""Pydantic schemas shared across endpoints."""

from typing import Optional
from pydantic import BaseModel, EmailStr


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


# Authentication schemas
class UserSignUp(BaseModel):
    username: str
    email: str
    password: str


class UserSignIn(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    token: str
    username: Optional[str] = None
