import requests

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"

CROP_INSIGHT_PROMPT = """
You are an agricultural planning assistant.

Given:
- Crop details
- Growth stage
- Irrigation schedule
- Current weather

Generate SHORT structured advice (5-7 lines ONLY):
- Use bullet points
- Use emojis naturally
- Keep farmer-friendly language
- Focus ONLY on action-based advice
- Do NOT exceed 8 lines

Be direct and practical. No long paragraphs.
""".strip()


def generate_crop_insight(crop_data, current_stage, weather_data, upcoming_irrigation):
    """
    Generate crop-specific insight using local Mistral.
    
    Args:
        crop_data: dict with crop_name, location, soil_type, sowing_date
        current_stage: str current growth stage
        weather_data: dict with current weather
        upcoming_irrigation: list of next 3 irrigation events
    
    Returns:
        str: Generated insight
    """
    irrigation_summary = []
    for irr in upcoming_irrigation[:3]:
        date = irr.get("date", "")[:10]
        amount = irr.get("waterAmountLiters", 0)
        irrigation_summary.append(f"{date}: {amount}L")
    
    irrigation_text = "\n".join(irrigation_summary) if irrigation_summary else "No upcoming irrigation"
    
    prompt = f"""{CROP_INSIGHT_PROMPT}

Crop: {crop_data.get('crop_name', 'Unknown')}
Location: {crop_data.get('location', 'Unknown')}
Soil Type: {crop_data.get('soil_type', 'Unknown')}
Current Stage: {current_stage or 'Not started'}

Weather Now:
Temperature: {weather_data.get('temp', 0)}°C
Humidity: {weather_data.get('humidity', 0)}%
Rain Chance: {weather_data.get('rain_chance', 0)}%

Upcoming Irrigation:
{irrigation_text}

Generate practical advice (max 7 lines):
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=30)
    except requests.RequestException:
        return "Mistral unavailable. Please check backend."

    if response.status_code != 200:
        return "Could not generate insight."

    try:
        data = response.json()
    except ValueError:
        return "Could not generate insight."

    return (data.get("response", "") if isinstance(data, dict) else "").strip()
