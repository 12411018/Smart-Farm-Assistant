"""Pydantic schemas shared across endpoints."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: str = ""
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
