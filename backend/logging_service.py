"""
Logging service for crop planning operations
Logs all yield input, irrigation, and calendar operations
"""

import json
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log files
YIELD_INPUT_LOG = LOG_DIR / "yield_input_log.json"
IRRIGATION_LOG = LOG_DIR / "irrigation_log.json"
CALENDAR_LOG = LOG_DIR / "calendar_log.json"
PLAN_OPERATIONS_LOG = LOG_DIR / "plan_operations.json"


def _ensure_log_file(log_file):
    """Ensure log file exists and is valid JSON."""
    if not log_file.exists():
        log_file.write_text(json.dumps([], indent=2))
    try:
        log_file.read_text()
    except json.JSONDecodeError:
        log_file.write_text(json.dumps([], indent=2))


def log_yield_input(user_id: str, crop_name: str, location: str, data: dict):
    """Log yield input submission."""
    _ensure_log_file(YIELD_INPUT_LOG)
    logs = json.loads(YIELD_INPUT_LOG.read_text())
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "userId": user_id,
        "cropName": crop_name,
        "location": location,
        "data": data,
    }
    logs.append(entry)
    YIELD_INPUT_LOG.write_text(json.dumps(logs, indent=2))
    print(f"[LOG] Yield input recorded: {crop_name} in {location}")


def log_plan_created(plan_id: str, user_id: str, crop_name: str, location: str):
    """Log crop plan creation."""
    _ensure_log_file(PLAN_OPERATIONS_LOG)
    logs = json.loads(PLAN_OPERATIONS_LOG.read_text())
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": "CREATE",
        "planId": plan_id,
        "userId": user_id,
        "cropName": crop_name,
        "location": location,
    }
    logs.append(entry)
    PLAN_OPERATIONS_LOG.write_text(json.dumps(logs, indent=2))
    print(f"[LOG] Plan created: {plan_id} - {crop_name}")


def log_plan_deleted(plan_id: str, user_id: str, crop_name: str):
    """Log crop plan deletion."""
    _ensure_log_file(PLAN_OPERATIONS_LOG)
    logs = json.loads(PLAN_OPERATIONS_LOG.read_text())
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": "DELETE",
        "planId": plan_id,
        "userId": user_id,
        "cropName": crop_name,
    }
    logs.append(entry)
    PLAN_OPERATIONS_LOG.write_text(json.dumps(logs, indent=2))
    print(f"[LOG] Plan deleted: {plan_id}")


def log_irrigation_adjustment(plan_id: str, date: str, original_amount: float, adjusted_amount: float, reason: str):
    """Log irrigation schedule adjustment."""
    _ensure_log_file(IRRIGATION_LOG)
    logs = json.loads(IRRIGATION_LOG.read_text())
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "planId": plan_id,
        "date": date,
        "originalAmount": original_amount,
        "adjustedAmount": adjusted_amount,
        "reason": reason,
    }
    logs.append(entry)
    IRRIGATION_LOG.write_text(json.dumps(logs, indent=2))
    print(f"[LOG] Irrigation adjusted for {plan_id}: {adjusted_amount}L ({reason})")


def log_calendar_view(plan_id: str, user_id: str, view_date: str):
    """Log calendar view/access."""
    _ensure_log_file(CALENDAR_LOG)
    logs = json.loads(CALENDAR_LOG.read_text())
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "planId": plan_id,
        "userId": user_id,
        "viewDate": view_date,
    }
    logs.append(entry)
    CALENDAR_LOG.write_text(json.dumps(logs, indent=2))
    print(f"[LOG] Calendar accessed for plan {plan_id}")


def get_all_logs():
    """Get all logs for dashboard."""
    _ensure_log_file(YIELD_INPUT_LOG)
    _ensure_log_file(IRRIGATION_LOG)
    _ensure_log_file(CALENDAR_LOG)
    _ensure_log_file(PLAN_OPERATIONS_LOG)
    
    return {
        "yieldInputLog": json.loads(YIELD_INPUT_LOG.read_text()),
        "irrigationLog": json.loads(IRRIGATION_LOG.read_text()),
        "calendarLog": json.loads(CALENDAR_LOG.read_text()),
        "planOperationsLog": json.loads(PLAN_OPERATIONS_LOG.read_text()),
    }
