import os
import requests
from datetime import datetime

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"
ONECALL_BASE = "https://api.openweathermap.org/data/3.0/onecall"
GEO_BASE = "https://api.openweathermap.org/geo/1.0/reverse"


def _get_api_key():
    return os.getenv("OPENWEATHER_API_KEY") or os.getenv("VITE_OPENWEATHER_API_KEY")


def _map_condition(code):
    if 200 <= code < 600:
        return "Rain"
    if 600 <= code < 700:
        return "Snow"
    if 700 <= code < 800:
        return "Clouds"
    if code == 800:
        return "Clear"
    return "Clouds"


def _format_hour(ts):
    return datetime.fromtimestamp(ts).strftime("%I:%M %p")


def _format_day(ts):
    return datetime.fromtimestamp(ts).strftime("%a")


def _fetch_location_label(lat, lon, api_key):
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": api_key,
    }
    try:
        response = requests.get(GEO_BASE, params=params, timeout=10)
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    try:
        data = response.json()
    except ValueError:
        return None

    if not isinstance(data, list) or not data:
        return None

    entry = data[0]
    city = entry.get("name")
    state = entry.get("state")
    country = entry.get("country")

    parts = [p for p in [city, state, country] if p]
    label = ", ".join(parts)

    return {
        "city": city,
        "state": state,
        "country": country,
        "label": label,
    }


def fetch_weather_data(lat, lon):
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY is not set")

    location = _fetch_location_label(lat, lon, api_key)

    # Try One Call (7-day + hourly)
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "exclude": "minutely,alerts",
    }
    response = requests.get(ONECALL_BASE, params=params, timeout=20)
    if response.ok:
        data = response.json()
        hourly = data.get("hourly", [])[:24]
        daily = data.get("daily", [])[:7]
        current = data.get("current", {})

        return {
            "current": {
                "temp": round(current.get("temp", 0)),
                "humidity": current.get("humidity", 0),
                "wind": current.get("wind_speed", 0),
                "rain": current.get("rain", {}).get("1h", 0),
                "rain_chance": round((hourly[0].get("pop", 0) if hourly else 0) * 100),
                "condition": _map_condition(current.get("weather", [{}])[0].get("id", 800)),
            },
            "hourly": [
                {
                    "time": _format_hour(h.get("dt", 0)),
                    "temp": round(h.get("temp", 0)),
                    "rain_chance": round(h.get("pop", 0) * 100),
                    "condition": _map_condition(h.get("weather", [{}])[0].get("id", 800)),
                }
                for h in hourly
            ],
            "daily": [
                {
                    "day": _format_day(d.get("dt", 0)),
                    "min": round(d.get("temp", {}).get("min", 0)),
                    "max": round(d.get("temp", {}).get("max", 0)),
                    "rain_chance": round(d.get("pop", 0) * 100),
                    "condition": _map_condition(d.get("weather", [{}])[0].get("id", 800)),
                    "rain": d.get("rain", 0),
                }
                for d in daily
            ],
            "location": location,
            "location_label": (location or {}).get("label") if location else None,
        }

    # Fallback to 5-day/3-hour forecast
    forecast_params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }
    forecast = requests.get(f"{OPENWEATHER_BASE}/forecast", params=forecast_params, timeout=20)
    if not forecast.ok:
        detail = forecast.text.strip() or "No response body"
        raise RuntimeError(f"Weather API error ({forecast.status_code}): {detail}")

    data = forecast.json()
    items = data.get("list", [])
    current_item = items[0] if items else {}

    hourly = items[:8]
    daily_map = {}
    for item in items:
        day_key = datetime.fromtimestamp(item["dt"]).strftime("%a")
        daily_map.setdefault(day_key, []).append(item)

    daily = []
    for day, entries in list(daily_map.items())[:7]:
        temps = [e["main"]["temp"] for e in entries]
        pops = [e.get("pop", 0) for e in entries]
        rain_sum = sum([e.get("rain", {}).get("3h", 0) for e in entries])
        daily.append(
            {
                "day": day,
                "min": round(min(temps)) if temps else 0,
                "max": round(max(temps)) if temps else 0,
                "rain_chance": round(max(pops) * 100) if pops else 0,
                "condition": _map_condition(entries[0]["weather"][0]["id"]) if entries else "Clouds",
                "rain": rain_sum,
            }
        )

    return {
        "current": {
            "temp": round(current_item.get("main", {}).get("temp", 0)),
            "humidity": current_item.get("main", {}).get("humidity", 0),
            "wind": current_item.get("wind", {}).get("speed", 0),
            "rain": current_item.get("rain", {}).get("3h", 0),
            "rain_chance": round(current_item.get("pop", 0) * 100),
            "condition": _map_condition(current_item.get("weather", [{}])[0].get("id", 800)),
        },
        "hourly": [
            {
                "time": _format_hour(h.get("dt", 0)),
                "temp": round(h.get("main", {}).get("temp", 0)),
                "rain_chance": round(h.get("pop", 0) * 100),
                "condition": _map_condition(h.get("weather", [{}])[0].get("id", 800)),
            }
            for h in hourly
        ],
        "daily": daily,
        "location": location,
        "location_label": (location or {}).get("label") if location else None,
    }
