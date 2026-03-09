"""
SQLAlchemy models for crop planning and irrigation system.
Production-ready version. Includes Chat History models (Conversation, Message)
for persistent conversation tracking.
"""

import uuid
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# =========================
# USER MODEL
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    auth_provider = Column(String(20), default="local")
    google_id = Column(String(255), unique=True, nullable=True)

    is_active = Column(Boolean, default=True)

    # Farm profile fields
    land_owned_acres = Column(Float, nullable=True)
    land_in_use_acres = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now())


# =========================
# CROP PLAN
# =========================

class CropPlan(Base):
    __tablename__ = "crop_plans"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    crop_name = Column(String(100))
    location = Column(String(150))
    soil_type = Column(String(100))

    sowing_date = Column(DateTime(timezone=True))
    growth_duration_days = Column(Integer)

    irrigation_method = Column(String(100))
    land_size_acres = Column(Float)

    status = Column(String(50), default="active")

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", backref="crop_plans")


# =========================
# CROP STAGE
# =========================

class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    crop_plan_id = Column(
        String(36),
        ForeignKey("crop_plans.id", ondelete="CASCADE")
    )

    stage = Column(String(100))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    duration_days = Column(Integer)
    recommended_irrigation_frequency_days = Column(Integer)

    crop_plan = relationship("CropPlan")


# =========================
# IRRIGATION SCHEDULE
# =========================

class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedule"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    crop_plan_id = Column(
        String(36),
        ForeignKey("crop_plans.id", ondelete="CASCADE")
    )

    date = Column(DateTime(timezone=True))
    stage = Column(String(100))

    water_amount_liters = Column(Integer)
    method = Column(String(100))

    status = Column(String(50), default="pending")

    crop_plan = relationship("CropPlan")


# =========================
# IRRIGATION LOG
# =========================

class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    crop_plan_id = Column(
        String(36),
        ForeignKey("crop_plans.id", ondelete="CASCADE")
    )

    irrigation_date = Column(Date)

    original_amount = Column(Float)
    adjusted_amount = Column(Float)

    status = Column(String(50), default="completed")

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    crop_plan = relationship("CropPlan")


# =========================
# WEATHER LOG
# =========================

class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_plan_id = Column(String(36), ForeignKey("crop_plans.id", ondelete="SET NULL"), index=True, nullable=True)
    weather_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    temp = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
    rain_chance = Column(Float, nullable=True)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    crop_plan = relationship("CropPlan", backref="weather_logs")


class Conversation(Base):
    """Chat conversation model for storing chat history."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    messages = relationship(
        "Message",
        cascade="all, delete-orphan",
        back_populates="conversation",
        passive_deletes=True,
        order_by="Message.timestamp",
    )


class Message(Base):
    """Chat message model for storing individual messages in a conversation."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tokens_used = Column(Integer, nullable=True, default=0)

    conversation = relationship("Conversation", back_populates="messages")
