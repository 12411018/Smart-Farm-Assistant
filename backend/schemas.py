"""Pydantic schemas shared across endpoints."""

from typing import Optional, List
from pydantic import BaseModel, EmailStr 
from datetime import datetime



class ChatRequest(BaseModel):
    message: str
    context: str = ""
    language: str = "en"  # User's selected language code (en, hi, mr, ta, te, kn, ml, gu, bn, pa)
    conversation_id: Optional[str] = None
    user_id: str = "default_user"


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

# Chat History Schemas
class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    message_count: Optional[int] = 0
    last_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    token: str
    username: Optional[str] = None
class ConversationDetailResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    user_id: str = "default_user"
    title: Optional[str] = "New Conversation"
