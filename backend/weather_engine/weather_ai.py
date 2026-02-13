import requests

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"

WEATHER_SYSTEM_PROMPT = """
You are an expert agricultural weather advisor.

You analyze weather data and give practical farming advice.

Keep answers:
- Short (max 7 lines unless needed)
- Structured
- Clear
- Action-oriented

Format:

a Weather Summary
b Irrigation Advice
c Risk Alerts
d Recommended Action

Use emojis properly.
No long paragraphs.
No generic text.
No repetition.
No markdown symbols like **.
""".strip()


def generate_weather_advice(weather, rules):
    prompt = f"""
{WEATHER_SYSTEM_PROMPT}

Weather Data:
Temperature: {weather['current']['temp']}°C
Humidity: {weather['current']['humidity']}%
Rain Chance: {weather['current']['rain_chance']}%
Wind Speed: {weather['current']['wind']} m/s

Rules:
Irrigation: {rules['irrigation']} ({rules['irrigation_reason']})
Pest Risk: {rules['pest_risk']}
Disease Risk: {rules['disease_risk']}
Spray Warning: {rules['spray_warning']}
Fertilizer Warning: {rules['fertilizer_warning']}

Generate clear structured advice.
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=30)
    except requests.RequestException:
        return ""

    if response.status_code != 200:
        return ""

    try:
        data = response.json()
    except ValueError:
        return ""

    return (data.get("response", "") if isinstance(data, dict) else "").strip()
