from datetime import datetime, timedelta, timezone
from services.irrigation_engine import calculate_water_liters
from .crop_data import CROP_STAGES, IRRIGATION_FREQUENCY, WATER_REQUIREMENTS


def generate_crop_stages(crop_name, sowing_date_str):
    """Generate growth stages with dates."""
    if crop_name not in CROP_STAGES:
        return []

    sowing_date = datetime.fromisoformat(sowing_date_str)
    stages = []
    current_date = sowing_date

    for stage_info in CROP_STAGES[crop_name]:
        start_date = current_date
        end_date = current_date + timedelta(days=stage_info["duration_days"])
        
        stages.append({
            "stage": stage_info["stage"],
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "durationDays": stage_info["duration_days"],
            "recommendedIrrigationFrequencyDays": IRRIGATION_FREQUENCY.get(stage_info["stage"], 7),
        })
        
        current_date = end_date

    return stages


def calculate_total_duration(crop_name):
    """Calculate total crop duration in days."""
    if crop_name not in CROP_STAGES:
        return 120  # Default
    
    return sum(stage["duration_days"] for stage in CROP_STAGES[crop_name])


def generate_irrigation_schedule(crop_name, sowing_date_str, land_size_acres, irrigation_method, stages):
    """Generate complete irrigation schedule."""
    if crop_name not in WATER_REQUIREMENTS:
        return []
    schedule = []

    for stage in stages:
        stage_start = datetime.fromisoformat(stage["startDate"])
        stage_end = datetime.fromisoformat(stage["endDate"])
        frequency_days = stage["recommendedIrrigationFrequencyDays"]

        current_date = stage_start
        while current_date <= stage_end:
            water_amount = calculate_water_liters(stage["stage"], land_size_acres)
            
            schedule.append({
                "date": current_date.isoformat(),
                "stage": stage["stage"],
                "waterAmountLiters": round(water_amount),
                "method": irrigation_method,
                "status": "pending",
            })
            
            current_date += timedelta(days=frequency_days)

    return schedule


def get_current_stage(stages):
    """Get current growth stage based on today's date."""
    now = datetime.now(timezone.utc)

    for stage in stages:
        start = datetime.fromisoformat(stage["startDate"])
        end = datetime.fromisoformat(stage["endDate"])

        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        if start <= now <= end:
            return stage["stage"]

    return None


def adjust_irrigation_for_weather(schedule_item, weather_data):
    """
    Adjust irrigation based on weather forecast.
    Returns: (adjusted_amount, adjustment_reason)
    """
    original_amount = schedule_item["waterAmountLiters"]
    adjusted_amount = original_amount
    reasons = []

    # Rain forecast adjustment
    rain_chance = weather_data.get("rain_chance", 0)
    if rain_chance > 60:
        adjusted_amount = 0
        reasons.append("Skipped: Rain forecast >60%")
    elif rain_chance > 40:
        adjusted_amount *= 0.5
        reasons.append("Reduced 50%: Rain forecast 40-60%")

    # Temperature adjustment
    temp = weather_data.get("temp", 25)
    if temp > 38:
        adjusted_amount *= 1.15
        reasons.append("Increased 15%: High temperature >38°C")
    elif temp > 35:
        adjusted_amount *= 1.10
        reasons.append("Increased 10%: High temperature >35°C")

    # Humidity adjustment
    humidity = weather_data.get("humidity", 50)
    if humidity > 80:
        adjusted_amount *= 0.90
        reasons.append("Reduced 10%: High humidity >80%")

    adjustment_reason = "; ".join(reasons) if reasons else "No adjustment needed"
    
    return round(adjusted_amount), adjustment_reason
