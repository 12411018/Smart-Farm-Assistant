"""Irrigation decision and schedule generation."""

from datetime import datetime, timedelta, timezone, date
from typing import Iterable, List, Optional
from sqlalchemy.orm import Session
from models import IrrigationSchedule, CropStage
from crop_engine.intelligence import compute_water_liters


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _stage_for_date(stages: Iterable[CropStage], day: datetime) -> Optional[CropStage]:
    day_date = _as_date(day) or _as_date(datetime.now(timezone.utc))
    for stage in stages:
        start = _as_date(stage.start_date)
        end = _as_date(stage.end_date)
        if start and end and start <= day_date <= end:
            return stage
    return None


def generate_irrigation_schedule(db: Session, plan, stages: List[CropStage], weather_current: Optional[dict] = None, moisture_value: Optional[float] = None, days: int = 7) -> List[IrrigationSchedule]:
    """Generate and persist the next `days` irrigation entries starting today.
    Replaces future pending entries to keep table clean.
    """
    today_dt = datetime.now(timezone.utc)
    # Remove future pending entries to avoid duplicates
    (db.query(IrrigationSchedule)
        .filter(IrrigationSchedule.crop_plan_id == plan.id)
        .filter(IrrigationSchedule.date >= today_dt)
        .delete(synchronize_session=False))

    # If it is already wet (rainy or high soil moisture), skip today's irrigation and push watering to tomorrow.
    rain_chance = 0
    rain_amount = 0
    if weather_current:
        rain_chance = weather_current.get("rain_chance") or weather_current.get("rainChance") or 0
        rain_amount = weather_current.get("rain") or 0
    wet_today = (rain_chance >= 60) or (rain_amount >= 5) or (moisture_value is not None and moisture_value >= 0.8)

    new_rows = []
    for offset in range(days):
        day_dt = today_dt + timedelta(days=offset)
        stage_row = _stage_for_date(stages, day_dt)
        stage_name = stage_row.stage if stage_row else plan.irrigation_method or "General"
        water_liters = compute_water_liters(plan.crop_name, plan.soil_type, plan.land_size_acres, weather_current, moisture_value)

        status = "pending"
        auto_adjusted = False

        # Skip irrigation when it's already wet; still log the skipped day so history stays consistent.
        if wet_today and offset == 0:
            status = "skipped"
            auto_adjusted = True
            water_liters = 0

        # If the computed need is zero (e.g., moisture-based skip), mark as skipped for clarity.
        if water_liters <= 0:
            status = "skipped"
            auto_adjusted = True
            water_liters = 0

        row = IrrigationSchedule(
            crop_plan_id=plan.id,
            date=day_dt,
            stage=stage_name,
            water_amount_liters=round(water_liters),
            method=plan.irrigation_method,
            status=status,
            auto_adjusted=auto_adjusted,
        )
        new_rows.append(row)

    db.add_all(new_rows)
    db.commit()
    return new_rows
