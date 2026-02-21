"""Irrigation water recommendation engine."""


def calculate_water_liters(stage_name: str, land_size_acres: float, soil_type: str | None = None, weather: dict | None = None) -> float:
    stage_mm_map = {
        "Germination": 3,
        "Vegetative": 5,
        "Tillering": 6,
        "Flowering": 6,
        "Grain Filling": 4,
    }

    soil_factor_map = {
        "sandy": 1.20,
        "loamy": 1.00,
        "clay": 0.80,
        "black": 0.90,
    }

    def _soil_factor(soil: str | None) -> float:
        if not soil:
            return 1.0
        return soil_factor_map.get(soil.strip().lower(), 1.0)

    def _weather_factor(weather_payload: dict | None) -> float:
        if not weather_payload:
            return 1.0
        rain_amount = weather_payload.get("rain") or 0
        temp = weather_payload.get("temp") or weather_payload.get("temperature") or 0
        humidity = weather_payload.get("humidity") or 0
        wind = weather_payload.get("wind") or weather_payload.get("windSpeed") or 0

        if rain_amount >= 5:
            return 0.0

        factor = 1.0
        if temp > 35:
            factor *= 1.15
        if humidity < 30:
            factor *= 1.10
        if wind > 5:
            factor *= 1.05
        return factor

    mm = stage_mm_map.get(stage_name, 4)
    factor = _soil_factor(soil_type) * _weather_factor(weather)
    liters = mm * factor * 4046 * land_size_acres
    return round(liters, 2)
