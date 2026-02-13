def irrigation_decision(weather):
    rain_today = weather["current"]["rain"]
    humidity = weather["current"]["humidity"]
    temp = weather["current"]["temp"]
    wind = weather["current"]["wind"]

    if rain_today > 5:
        return {
            "irrigation": "SKIP",
            "reason": "Sufficient rainfall received today",
        }

    if humidity > 85 and temp < 28:
        return {
            "irrigation": "REDUCE",
            "reason": "High humidity reduces evapotranspiration",
        }

    if temp > 35 and wind > 4:
        return {
            "irrigation": "INCREASE",
            "reason": "High evapotranspiration conditions",
        }

    return {
        "irrigation": "NORMAL",
        "reason": "Standard irrigation recommended",
    }


def pest_risk(weather):
    temp = weather["current"]["temp"]
    humidity = weather["current"]["humidity"]
    if 28 <= temp <= 35 and 60 <= humidity <= 80:
        return "HIGH"
    if 24 <= temp < 28 and humidity >= 60:
        return "MEDIUM"
    return "LOW"


def disease_risk(weather):
    temp = weather["current"]["temp"]
    humidity = weather["current"]["humidity"]
    if humidity > 80 and 25 <= temp <= 30:
        return "HIGH"
    if humidity > 70 and 22 <= temp <= 32:
        return "MEDIUM"
    return "LOW"


def spray_warning(weather):
    wind = weather["current"]["wind"]
    if wind > 5:
        return "Avoid spraying; wind speed is high"
    return "Safe to spray with caution"


def fertilizer_warning(weather):
    heavy_rain = any(day.get("rain", 0) > 10 or day.get("rain_chance", 0) > 70 for day in weather["daily"])
    if heavy_rain:
        return "Heavy rain expected. Delay fertilizer application"
    return "No heavy rain expected; fertilizer application is safe"


def build_weather_rules(weather):
    irrigation = irrigation_decision(weather)
    return {
        "irrigation": irrigation["irrigation"],
        "irrigation_reason": irrigation["reason"],
        "pest_risk": pest_risk(weather),
        "disease_risk": disease_risk(weather),
        "spray_warning": spray_warning(weather),
        "fertilizer_warning": fertilizer_warning(weather),
    }
