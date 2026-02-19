"""Irrigation water recommendation engine."""


def calculate_water_liters(stage_name: str, land_size_acres: float) -> float:
    stage_mm_map = {
        "Germination": 3,
        "Vegetative": 5,
        "Tillering": 6,
        "Flowering": 6,
        "Grain Filling": 4,
    }

    mm = stage_mm_map.get(stage_name, 4)
    liters = mm * 4046 * land_size_acres
    return round(liters, 2)
