"""Crop intelligence utilities for water and environmental adjustments."""

from typing import Optional

BASE_WATER_REQUIREMENTS = {
    "Rice": 6.0,   # mm/day
    "Wheat": 4.5,  # mm/day
}

SOIL_IMPACT = {
    "black": 0.90,   # retains water, reduce 10%
    "sandy": 1.15,   # drains fast, increase 15%
}


def _normalize_soil(soil: Optional[str]) -> str:
    return (soil or "").strip().lower()


def base_water_mm(crop_name: str) -> float:
    return BASE_WATER_REQUIREMENTS.get(crop_name, 4.0)


def soil_factor(soil_type: Optional[str]) -> float:
    key = _normalize_soil(soil_type)
    return SOIL_IMPACT.get(key, 1.0)


def weather_factor(weather: Optional[dict]) -> float:
    if not weather:
        return 1.0
    factor = 1.0
    rain = weather.get("rain_chance") or weather.get("rainChance") or 0
    temp = weather.get("temp") or weather.get("temperature") or 0
    humidity = weather.get("humidity") or 0

    if rain > 60:
        factor *= 0.70  # reduce 30%
    if temp > 35:
        factor *= 1.15  # increase 15%
    if humidity < 25:
        factor *= 1.10  # increase 10%
    return factor


def adjust_by_moisture(sensor_value: Optional[float], threshold: float = 0.35) -> float:
    """Placeholder for future Arduino moisture input. Returns multiplicative factor."""
    if sensor_value is None:
        return 1.0
    if sensor_value < threshold:
        return 1.20  # increase irrigation
    if sensor_value > 0.80:
        return 0.0   # skip if very wet
    return 1.0


def compute_water_liters(crop_name: str, soil_type: Optional[str], land_size_acres: float, weather: Optional[dict] = None, moisture_value: Optional[float] = None) -> float:
    mm = base_water_mm(crop_name)
    factor = soil_factor(soil_type) * weather_factor(weather) * adjust_by_moisture(moisture_value)
    effective_mm = mm * factor
    liters = effective_mm * 4046 * land_size_acres
    return round(liters, 2)
