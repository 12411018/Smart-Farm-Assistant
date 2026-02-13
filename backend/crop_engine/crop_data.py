# Crop growth stage definitions
CROP_STAGES = {
    "Wheat": [
        {"stage": "Germination", "duration_days": 10},
        {"stage": "Vegetative", "duration_days": 35},
        {"stage": "Tillering", "duration_days": 30},
        {"stage": "Flowering", "duration_days": 25},
        {"stage": "Grain Filling", "duration_days": 20},
    ],
    "Rice": [
        {"stage": "Germination", "duration_days": 7},
        {"stage": "Vegetative", "duration_days": 40},
        {"stage": "Tillering", "duration_days": 30},
        {"stage": "Flowering", "duration_days": 30},
        {"stage": "Grain Filling", "duration_days": 33},
    ],
    "Cotton": [
        {"stage": "Germination", "duration_days": 10},
        {"stage": "Vegetative", "duration_days": 50},
        {"stage": "Flowering", "duration_days": 50},
        {"stage": "Boll Development", "duration_days": 50},
        {"stage": "Maturation", "duration_days": 20},
    ],
    "Sugarcane": [
        {"stage": "Germination", "duration_days": 30},
        {"stage": "Tillering", "duration_days": 60},
        {"stage": "Grand Growth", "duration_days": 120},
        {"stage": "Maturation", "duration_days": 60},
    ],
    "Maize": [
        {"stage": "Germination", "duration_days": 7},
        {"stage": "Vegetative", "duration_days": 35},
        {"stage": "Tasseling", "duration_days": 15},
        {"stage": "Silking", "duration_days": 20},
        {"stage": "Grain Filling", "duration_days": 23},
    ],
    "Tomato": [
        {"stage": "Germination", "duration_days": 7},
        {"stage": "Vegetative", "duration_days": 30},
        {"stage": "Flowering", "duration_days": 20},
        {"stage": "Fruit Development", "duration_days": 30},
        {"stage": "Ripening", "duration_days": 13},
    ],
}

# Irrigation frequency by stage (in days)
IRRIGATION_FREQUENCY = {
    "Germination": 4,
    "Vegetative": 7,
    "Tillering": 7,
    "Flowering": 5,
    "Grain Filling": 8,
    "Boll Development": 6,
    "Maturation": 10,
    "Grand Growth": 5,
    "Tasseling": 5,
    "Silking": 4,
    "Fruit Development": 4,
    "Ripening": 6,
}

# Water amount by crop and method (liters per acre per day)
WATER_REQUIREMENTS = {
    "Wheat": {"Drip": 2500, "Sprinkler": 3000, "Flood": 5000},
    "Rice": {"Drip": 4000, "Sprinkler": 4500, "Flood": 8000},
    "Cotton": {"Drip": 2000, "Sprinkler": 2500, "Flood": 4000},
    "Sugarcane": {"Drip": 3500, "Sprinkler": 4000, "Flood": 7000},
    "Maize": {"Drip": 2200, "Sprinkler": 2700, "Flood": 4500},
    "Tomato": {"Drip": 1800, "Sprinkler": 2200, "Flood": 3500},
}
