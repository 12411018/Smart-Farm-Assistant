"""Database service helpers for crop plans and irrigation."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from models import CropPlan, CropStage, IrrigationSchedule, IrrigationLog
from crop_engine.crop_planner import (
    adjust_irrigation_for_weather,
    calculate_total_duration,
    generate_crop_stages,
    generate_irrigation_schedule,
)


def _parse_iso(dt_str: str) -> datetime:
    value = datetime.fromisoformat(dt_str)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def _to_iso(dt_obj: datetime) -> str:
    return dt_obj.isoformat()


def serialize_stage(stage: CropStage) -> Dict:
    return {
        "id": str(stage.id),
        "stage": stage.stage,
        "startDate": _to_iso(stage.start_date),
        "endDate": _to_iso(stage.end_date),
        "durationDays": stage.duration_days,
        "recommendedIrrigationFrequencyDays": stage.recommended_irrigation_frequency_days,
    }


def serialize_schedule(item: IrrigationSchedule) -> Dict:
    return {
        "id": str(item.id),
        "cropPlanId": str(item.crop_plan_id),
        "date": _to_iso(item.date),
        "stage": item.stage,
        "waterAmountLiters": item.water_amount_liters,
        "method": item.method,
        "status": item.status,
        "autoAdjusted": item.auto_adjusted,
    }


def serialize_plan(plan: CropPlan, stages: List[CropStage], schedule: List[IrrigationSchedule]) -> Dict:
    return {
        "id": str(plan.id),
        "userId": plan.user_id,
        "cropName": plan.crop_name,
        "location": plan.location,
        "soilType": plan.soil_type,
        "sowingDate": _to_iso(plan.sowing_date),
        "growthDurationDays": plan.growth_duration_days,
        "irrigationMethod": plan.irrigation_method,
        "landSizeAcres": plan.land_size_acres,
        "expectedInvestment": plan.expected_investment,
        "waterSourceType": plan.water_source_type,
        "status": plan.status,
        "createdAt": _to_iso(plan.created_at),
        "stages": [serialize_stage(s) for s in stages],
        "irrigationSchedule": [serialize_schedule(s) for s in schedule],
    }


def create_crop_plan(db: Session, payload: Dict) -> Tuple[Dict, List[Dict], List[Dict], int]:
    total_duration = calculate_total_duration(payload["cropName"])
    stages_data = generate_crop_stages(payload["cropName"], payload["sowingDate"])
    schedule_data = generate_irrigation_schedule(
        payload["cropName"],
        payload["sowingDate"],
        payload["landSizeAcres"],
        payload["irrigationMethod"],
        stages_data,
    )

    plan = CropPlan(
        user_id=payload["userId"],
        crop_name=payload["cropName"],
        location=payload["location"],
        soil_type=payload["soilType"],
        sowing_date=_parse_iso(payload["sowingDate"]),
        growth_duration_days=total_duration,
        irrigation_method=payload["irrigationMethod"],
        land_size_acres=payload["landSizeAcres"],
        expected_investment=payload.get("expectedInvestment"),
        water_source_type=payload.get("waterSourceType"),
        status="active",
    )
    db.add(plan)
    db.flush()

    stage_rows = []
    for stage in stages_data:
        row = CropStage(
            crop_plan_id=plan.id,
            stage=stage["stage"],
            start_date=_parse_iso(stage["startDate"]),
            end_date=_parse_iso(stage["endDate"]),
            duration_days=stage["durationDays"],
            recommended_irrigation_frequency_days=stage["recommendedIrrigationFrequencyDays"],
        )
        stage_rows.append(row)
    db.add_all(stage_rows)

    schedule_rows = []
    for item in schedule_data:
        row = IrrigationSchedule(
            crop_plan_id=plan.id,
            date=_parse_iso(item["date"]),
            stage=item["stage"],
            water_amount_liters=item["waterAmountLiters"],
            method=item["method"],
            status=item.get("status", "pending"),
        )
        schedule_rows.append(row)
    db.add_all(schedule_rows)
    db.commit()

    db.refresh(plan)
    return serialize_plan(plan, stage_rows, schedule_rows), stages_data, schedule_data, total_duration


def fetch_crop_plan(db: Session, crop_plan_id: str) -> Tuple[CropPlan, List[CropStage], List[IrrigationSchedule]]:
    plan_uuid = uuid.UUID(crop_plan_id)
    plan = db.get(CropPlan, plan_uuid)
    if plan is None:
        return None, [], []
    stages = (
        db.query(CropStage)
        .filter(CropStage.crop_plan_id == plan_uuid)
        .order_by(CropStage.start_date)
        .all()
    )
    schedule = (
        db.query(IrrigationSchedule)
        .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
        .order_by(IrrigationSchedule.date)
        .all()
    )
    return plan, stages, schedule


def list_user_plans(db: Session, user_id: str) -> List[CropPlan]:
    return (
        db.query(CropPlan)
        .filter(CropPlan.user_id == user_id)
        .filter(CropPlan.status == "active")
        .order_by(CropPlan.created_at.desc())
        .all()
    )


def delete_plan(db: Session, crop_plan_id: str) -> Tuple[CropPlan, str, str]:
    plan_uuid = uuid.UUID(crop_plan_id)
    plan = db.get(CropPlan, plan_uuid)
    if plan is None:
        return None, None, None
    user_id = plan.user_id
    crop_name = plan.crop_name
    db.delete(plan)
    db.commit()
    return plan, user_id, crop_name


def adjust_schedule_for_weather(db: Session, crop_plan_id: str, weather_current: Dict, limit: int = 7) -> List[Dict]:
    plan_uuid = uuid.UUID(crop_plan_id)
    today = datetime.now(timezone.utc)
    schedules = (
        db.query(IrrigationSchedule)
        .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
        .filter(IrrigationSchedule.status == "pending")
        .filter(IrrigationSchedule.date >= today)
        .order_by(IrrigationSchedule.date)
        .limit(limit)
        .all()
    )

    adjustments = []
    for item in schedules:
        adjusted_amount, reason = adjust_irrigation_for_weather(
            {
                "waterAmountLiters": item.water_amount_liters,
                "stage": item.stage,
                "date": _to_iso(item.date),
            },
            weather_current,
        )
        original = item.water_amount_liters
        item.water_amount_liters = adjusted_amount
        item.auto_adjusted = True

        log_entry = IrrigationLog(
            crop_plan_id=plan_uuid,
            date=item.date,
            original_amount=original,
            adjusted_amount=adjusted_amount,
            weather_adjustment=reason,
            auto_triggered=True,
        )
        db.add(log_entry)
        adjustments.append(
            {
                "date": _to_iso(item.date),
                "originalAmount": original,
                "adjustedAmount": adjusted_amount,
                "reason": reason,
            }
        )

    db.commit()
    return adjustments


def fetch_irrigation_logs(db: Session, crop_plan_id: str, limit: int = 20) -> List[IrrigationLog]:
    plan_uuid = uuid.UUID(crop_plan_id)
    return (
        db.query(IrrigationLog)
        .filter(IrrigationLog.crop_plan_id == plan_uuid)
        .order_by(IrrigationLog.created_at.desc())
        .limit(limit)
        .all()
    )
