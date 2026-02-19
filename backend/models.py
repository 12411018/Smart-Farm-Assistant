"""SQLAlchemy models for crop planning and irrigation."""

import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CropPlan(Base):
    __tablename__ = "crop_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    crop_name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False)
    soil_type = Column(String, nullable=False)
    sowing_date = Column(DateTime(timezone=True), nullable=False)
    growth_duration_days = Column(Integer, nullable=False)
    irrigation_method = Column(String, nullable=False)
    land_size_acres = Column(Float, nullable=False)
    expected_investment = Column(Float, nullable=True)
    water_source_type = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    stages = relationship(
        "CropStage",
        cascade="all, delete-orphan",
        back_populates="crop_plan",
        passive_deletes=True,
    )
    irrigation_schedule = relationship(
        "IrrigationSchedule",
        cascade="all, delete-orphan",
        back_populates="crop_plan",
        passive_deletes=True,
    )
    irrigation_logs = relationship(
        "IrrigationLog",
        cascade="all, delete-orphan",
        back_populates="crop_plan",
        passive_deletes=True,
    )
    weather_logs = relationship(
        "WeatherLog",
        cascade="all, delete-orphan",
        back_populates="crop_plan",
        passive_deletes=True,
    )


class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_plan_id = Column(UUID(as_uuid=True), ForeignKey("crop_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    stage = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_days = Column(Integer, nullable=False)
    recommended_irrigation_frequency_days = Column(Integer, nullable=False)

    crop_plan = relationship("CropPlan", back_populates="stages")


class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_plan_id = Column(UUID(as_uuid=True), ForeignKey("crop_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    date = Column(DateTime(timezone=True), index=True, nullable=False)
    stage = Column(String, nullable=False)
    water_amount_liters = Column(Integer, nullable=False)
    method = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    auto_adjusted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    crop_plan = relationship("CropPlan", back_populates="irrigation_schedule")


class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_plan_id = Column(UUID(as_uuid=True), ForeignKey("crop_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    original_amount = Column(Integer, nullable=False)
    adjusted_amount = Column(Integer, nullable=False)
    weather_adjustment = Column(Text, nullable=True)
    auto_triggered = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    crop_plan = relationship("CropPlan", back_populates="irrigation_logs")


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_plan_id = Column(UUID(as_uuid=True), ForeignKey("crop_plans.id", ondelete="SET NULL"), index=True, nullable=True)
    weather_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    temp = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
    rain_chance = Column(Float, nullable=True)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    crop_plan = relationship("CropPlan", back_populates="weather_logs")
