import os
import uuid
import requests
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from vectorstore.search import RAGSearch, build_context_text
from multilingual_pipeline import process_multilingual_query, set_rag_pipeline
from weather_engine.weather_service import fetch_weather_data
from weather_engine.weather_rules import build_weather_rules
from weather_engine.weather_ai import generate_weather_advice
from crop_engine.crop_planner import (
    get_current_stage,
)
from crop_engine.intelligence import compute_water_liters
from crop_engine.crop_insights import generate_crop_insight
from firebase_config import get_firestore, is_firebase_enabled
from logging_service import log_yield_input, log_plan_created, log_plan_deleted, log_irrigation_adjustment, get_all_logs
from database import get_db
from models import CropStage, IrrigationSchedule, IrrigationLog, CropPlan
from services.crop_status_engine import calculate_crop_status
from irrigation_engine.decision import generate_irrigation_schedule
from services.crop_service import (
    adjust_schedule_for_weather,
    create_crop_plan as create_crop_plan_db,
    fetch_crop_plan,
    list_user_plans,
    serialize_plan,
    serialize_schedule,
    serialize_stage,
    delete_plan as delete_plan_db,
    fetch_irrigation_logs,
)
from schemas import ChatRequest, WeatherRequest, CropPlanRequest

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
# Default to mistral:latest since it is installed locally; override via OLLAMA_MODEL env when needed.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """
You are a smart, friendly farming assistant 🌾🚜 helping farmers.

Personality:
- Sounds like a real field expert
- Warm, confident, practical
- Farmer-friendly, not academic

Answer style rules:
- Keep answers SHORT and USEFUL
- 5–7 lines for simple questions
- More detail ONLY if question is complex
- Use bullet points when helpful
- Use emojis naturally 😊🌱💧🌾🚜
- Start with the MOST IMPORTANT point
- Explain WHY briefly
- For government schemes, provide comprehensive information (don't limit to 5 if more are relevant)


CONTEXT FILTERING (CRITICAL):
- The retrieved context may contain some irrelevant or noisy information
- ONLY use context that is DIRECTLY relevant to the user's specific question
- IGNORE any context that doesn't clearly relate to the query
- If the context is noisy or unrelated, rely on your general farming knowledge
- DO NOT mention irrelevant topics from the context in your answer

Location handling:
- If user mentions a location, use it
- If not mentioned, give general Indian advice
- Do NOT assume Maharashtra automatically
- Ask ONE short follow-up question only if required

NEVER:
- Say you are an AI or language model
- Mention embeddings, RAG, vector DB, or internal systems
- Dump long unstructured paragraphs
- Repeat generic textbook explanations

Goal:
Farmers should feel:
"This assistant understands my farm."
""".strip()

app = FastAPI(title="Smart Farming Assistant API")
    
        # Cache last exchanges for lightweight history; if model is unavailable, return the generated reply above.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


rag_search = RAGSearch()
chat_history = []


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _start_of_day(dt: datetime) -> datetime:
    return datetime.combine(dt.date(), datetime.min.time(), tzinfo=timezone.utc)


def _compute_weather_adjustment(weather: dict | None):
    """Return (factor, reason, should_skip)."""
    if not weather:
        return 1.0, "No weather data", False

    rain_amount = weather.get("rain") or 0
    rain_chance = weather.get("rain_chance") or weather.get("rainChance") or 0
    temp = weather.get("temp") or weather.get("temperature") or 0
    humidity = weather.get("humidity") or 0
    wind = weather.get("wind") or weather.get("windSpeed") or 0

    # Skip when both amount and probability are strong.
    if rain_amount >= 5 and rain_chance >= 70:
        return 0.0, f"Skip: rain {rain_amount}mm @ {rain_chance}%", True

    factor = 1.0
    reasons = []

    # Reduce slightly in cool + very humid conditions
    if humidity > 85 and temp < 25:
        factor *= 0.8
        reasons.append("Reduce 20%: humid>85% & temp<25C")

    if temp > 35:
        factor *= 1.15
        reasons.append("Increase 15%: temp>35C")
    if humidity < 30:
        factor *= 1.10
        reasons.append("Increase 10%: humidity<30%")
    if wind > 5:
        factor *= 1.05
        reasons.append("Increase 5%: wind>5 m/s")

    return factor, "; ".join(reasons) if reasons else "No adjustment", False


def _mark_missed_irrigations(db: Session):
    """Mark past-due pending irrigations as missed and log them."""
    start_today = _start_of_day(datetime.now(timezone.utc))
    missed = (
        db.query(IrrigationSchedule)
        .filter(IrrigationSchedule.status == "pending")
        .filter(IrrigationSchedule.date < start_today)
        .all()
    )

    for entry in missed:
        entry.status = "missed"
        entry.actual_liters = entry.actual_liters or 0
        entry.executed_at = entry.executed_at or datetime.now(timezone.utc)
        log_row = IrrigationLog(
            crop_plan_id=entry.crop_plan_id,
            irrigation_date=_as_date(entry.date),
            original_amount=entry.water_amount_liters,
            adjusted_amount=entry.water_amount_liters,
            weather_adjustment="Marked missed",
            auto_triggered=True,
            planned_liters=entry.water_amount_liters,
            actual_liters=0,
            duration_seconds=0,
            status="missed",
            weather_adjustment_percent=entry.weather_adjustment_percent or 0,
        )
        db.add(log_row)

    if missed:
        db.commit()


def _sync_plan_to_firestore(db_client, crop_plan_id: str, plan_data: dict, stages: list, irrigation_schedule: list) -> bool:
    """Persist plan data to Firestore for compatibility."""
    if db_client is None:
        return False
    try:
        plan_payload = {
            "userId": plan_data.get("userId"),
            "cropName": plan_data.get("cropName"),
            "location": plan_data.get("location"),
            "soilType": plan_data.get("soilType"),
            "sowingDate": plan_data.get("sowingDate"),
            "growthDurationDays": plan_data.get("growthDurationDays"),
            "irrigationMethod": plan_data.get("irrigationMethod"),
            "landSizeAcres": plan_data.get("landSizeAcres"),
            "expectedInvestment": plan_data.get("expectedInvestment"),
            "waterSourceType": plan_data.get("waterSourceType"),
            "createdAt": plan_data.get("createdAt", datetime.now().isoformat()),
            "status": plan_data.get("status", "active"),
        }
        crop_plan_ref = db_client.collection("crop_plans").document(crop_plan_id)
        crop_plan_ref.set(plan_payload)

        for stage in stages:
            db_client.collection("crop_calendar").add({"cropPlanId": crop_plan_id, **stage})

        for schedule_item in irrigation_schedule:
            db_client.collection("irrigation_schedule").add({"cropPlanId": crop_plan_id, **schedule_item})
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[WARNING] Firebase sync failed for plan {crop_plan_id}: {exc}")
        return False


def _format_history(limit: int = 6) -> str:
    if not chat_history:
        return ""
    recent = chat_history[-limit:]
    lines = []
    for item in recent:
        role = "Farmer" if item["role"] == "user" else "Assistant"
        lines.append(f"{role}: {item['content']}")
    return "\n".join(lines).strip()


def _build_prompt(user_message: str, context_text: str, history_text: str) -> str:
    history_block = f"Conversation so far:\n{history_text}\n----------------\n" if history_text else ""
    context_block = f"Retrieved context (may contain noise - use only relevant parts):\n{context_text}\n----------------\n" if context_text else ""
    return (
        f"{SYSTEM_PROMPT}\n----------------\n{context_block}"
        f"{history_block}User question:\n{user_message}"
    ).strip()


def generate_reply(user_message: str) -> str:
    """Generate reply using local Ollama Mistral model."""
    try:
        # Retrieve 5 chunks for better context coverage while filtering noise
        chunks = rag_search.retrieve_context(user_message, top_k=8)
        context_text = build_context_text(chunks)
    except Exception:
        context_text = ""

    history_text = _format_history()

    prompt = _build_prompt(user_message, context_text, history_text)
    headers = {"Content-Type": "application/json"}

    def _invoke_model(model_name: str):
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            # Constrain generation to reduce latency and resource use.
            "options": {
                # Increased token limit to allow detailed answers for complex queries
                "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "256")),
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.35")),
                "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
                "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "2048")),
            },
        }
        try:
            response = requests.post(
                OLLAMA_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=180,
            )
        except requests.RequestException as exc:
            return None, f"Model error: {exc}"

        if response.status_code != 200:
            try:
                error_json = response.json()
                error_message = error_json.get("error") or response.text
            except ValueError:
                error_message = response.text
            return None, error_message

        try:
            data = response.json()
        except ValueError:
            return None, "Model error: Invalid JSON response"

        generated_text = data.get("response", "") if isinstance(data, dict) else ""
        if not generated_text:
            return None, "Model error: Empty response from model"

        return generated_text.strip(), None

    primary_model = OLLAMA_MODEL
    fallback_model = os.getenv("OLLAMA_FALLBACK_MODEL", "phi3:mini")

    reply, error_message = _invoke_model(primary_model)

    if error_message:
        lowered = error_message.lower()
        memory_or_missing = ("system memory" in lowered) or ("not enough" in lowered) or ("not found" in lowered)

        if memory_or_missing and fallback_model and fallback_model != primary_model:
            fallback_reply, fallback_error = _invoke_model(fallback_model)
            if fallback_reply:
                reply = f"[Using fallback model {fallback_model}] {fallback_reply}"
                chat_history.append({"role": "user", "content": user_message})
                chat_history.append({"role": "assistant", "content": reply})
                return reply
            if fallback_error:
                error_message = fallback_error

        if "not found" in lowered:
            return (
                "Model unavailable: Ollama cannot find the requested model. "
                f"Pull it with 'ollama pull {primary_model}' or set OLLAMA_MODEL to an installed model."
            )
        if "system memory" in lowered or "not enough" in lowered:
            return (
                "Model unavailable: local model needs more RAM. "
                "Set OLLAMA_MODEL to a smaller model (e.g., phi3:mini) and restart the backend."
            )
        return f"Model error: {error_message}"

    # Cache last exchanges for lightweight history; if model is unavailable, return the generated reply above.
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": reply})

    return reply


set_rag_pipeline(generate_reply)


def generate_reply_direct(user_message: str) -> str:
    """Fast path: call Ollama directly without RAG/history for lowest latency."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": user_message,
        "stream": False,
        "options": {
            "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "96")),
            "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.35")),
            "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "1024")),
        },
    }

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        return f"Model error: {exc}"

    if response.status_code != 200:
        try:
            err_json = response.json()
            err_msg = err_json.get("error") or response.text
        except ValueError:
            err_msg = response.text
        return f"Model error: {err_msg}"

    try:
        data = response.json()
    except ValueError:
        return "Model error: Invalid JSON response"

    text = data.get("response", "") if isinstance(data, dict) else ""
    if not text:
        return "Model error: Empty response from model"

    return text.strip()


@app.post("/chat")
def chat(req: ChatRequest):
    """Chat endpoint for agriculture advice"""
    reply = process_multilingual_query(req.message, req.language)
    return {"reply": reply}


@app.post("/chat/direct")
def chat_direct(req: ChatRequest):
    """Chat endpoint without RAG/history for fastest local model response."""
    reply = generate_reply_direct(req.message)
    return {"reply": reply}


@app.post("/weather-analysis")
def weather_analysis(req: WeatherRequest):
    """Weather intelligence pipeline endpoint."""
    try:
        weather = fetch_weather_data(req.lat, req.lon)
        rules = build_weather_rules(weather)
        ai_advice = ""
        if req.include_ai:
            ai_advice = generate_weather_advice(weather, rules)
        return {
            "weather": weather,
            "rules": rules,
            "ai_advice": ai_advice,
        }
    except Exception as exc:
        return {
            "weather": None,
            "rules": None,
            "ai_advice": "",
            "error": str(exc),
        }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/crop-plan/create")
def create_crop_plan(req: CropPlanRequest, db: Session = Depends(get_db)):
    """Create new crop plan with calendar and irrigation schedule (PostgreSQL first, Firebase mirrored)."""
    try:
        plan_data, stages, irrigation_schedule, total_duration = create_crop_plan_db(db, req.dict())
        firebase_db = get_firestore()
        firebase_enabled = _sync_plan_to_firestore(firebase_db, plan_data["id"], plan_data, stages, irrigation_schedule)

        log_plan_created(plan_data["id"], req.userId, req.cropName, req.location)

        return {
            "success": True,
            "cropPlanId": plan_data["id"],
            "stages": stages,
            "irrigationSchedule": irrigation_schedule,
            "totalDurationDays": total_duration,
            "firebaseEnabled": firebase_enabled,
        }

    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] Failed to create crop plan: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-plan/{crop_plan_id}")
def get_crop_plan(crop_plan_id: str, db: Session = Depends(get_db)):
    """Get crop plan details with calendar and schedule from PostgreSQL."""
    try:
        plan, stage_rows, schedule_rows = fetch_crop_plan(db, crop_plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        stages = [serialize_stage(s) for s in stage_rows]
        schedule = [serialize_schedule(s) for s in schedule_rows]
        status = calculate_crop_status(plan, stage_rows)

        return {
            "cropPlan": serialize_plan(plan, stage_rows, schedule_rows),
            "calendar": stages,
            "irrigationSchedule": schedule,
            "currentStage": status["current_stage"],
            "overallStatus": status["overall_status"],
            "daysPassed": status["days_passed"],
            "progressPercent": status["progress"],
        }

    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-plan/user/{user_id}")
def get_user_crop_plans(user_id: str, db: Session = Depends(get_db)):
    """Get all crop plans for a user from PostgreSQL (Firebase flag for compatibility)."""
    try:
        plans = list_user_plans(db, user_id)
        response = []
        today = datetime.now(timezone.utc)
        for plan in plans:
            stages = (
                db.query(CropStage)
                .filter(CropStage.crop_plan_id == plan.id)
                .order_by(CropStage.start_date)
                .all()
            )
            schedule_next = (
                db.query(IrrigationSchedule)
                .filter(IrrigationSchedule.crop_plan_id == plan.id)
                .filter(IrrigationSchedule.date >= today)
                .order_by(IrrigationSchedule.date)
                .first()
            )

            status = calculate_crop_status(plan, stages)

            response.append(
                {
                    "id": str(plan.id),
                    "cropName": plan.crop_name,
                    "location": plan.location,
                    "soilType": plan.soil_type,
                    "sowingDate": plan.sowing_date.isoformat(),
                    "growthDurationDays": plan.growth_duration_days,
                    "irrigationMethod": plan.irrigation_method,
                    "landSizeAcres": plan.land_size_acres,
                    "expectedInvestment": plan.expected_investment,
                    "waterSourceType": plan.water_source_type,
                    "status": plan.status,
                    "currentStage": status["current_stage"],
                    "daysPassed": status["days_passed"],
                    "overallStatus": status["overall_status"],
                    "progressPercent": status["progress"],
                    "nextIrrigationDate": schedule_next.date.isoformat() if schedule_next else None,
                }
            )

        return {"plans": response, "firebaseEnabled": is_firebase_enabled()}

    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/irrigation/adjust")
def adjust_irrigation_schedule(crop_plan_id: str, lat: float, lon: float, db: Session = Depends(get_db)):
    """Adjust upcoming irrigation based on weather and log changes (persist to PostgreSQL, optional Firebase mirror)."""
    try:
        weather = fetch_weather_data(lat, lon)
        current_weather = weather["current"]

        adjustments = adjust_schedule_for_weather(db, crop_plan_id, current_weather)
        for adj in adjustments:
            log_irrigation_adjustment(
                crop_plan_id,
                adj["date"],
                adj["originalAmount"],
                adj["adjustedAmount"],
                adj["reason"],
            )

        return {"adjustments": adjustments, "firebaseEnabled": is_firebase_enabled()}

    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-insight/{crop_plan_id}")
def get_crop_insight(crop_plan_id: str, lat: float, lon: float, db: Session = Depends(get_db)):
    """Generate AI-powered crop insight using PostgreSQL data."""
    try:
        plan, stage_rows, schedule_rows = fetch_crop_plan(db, crop_plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        stages = [serialize_stage(s) for s in stage_rows]
        current_stage = get_current_stage(stages)

        now = datetime.now(timezone.utc)
        upcoming_irrigation = [
            serialize_schedule(s)
            for s in schedule_rows
            if s.status == "pending" and s.date >= now
        ][:3]

        weather = fetch_weather_data(lat, lon)
        current_weather = weather["current"]

        insight = generate_crop_insight(
            crop_data={
                "crop_name": plan.crop_name,
                "location": plan.location,
                "soil_type": plan.soil_type,
                "sowing_date": plan.sowing_date.isoformat(),
            },
            current_stage=current_stage,
            weather_data=current_weather,
            upcoming_irrigation=upcoming_irrigation,
        )

        return {
            "insight": insight,
            "currentStage": current_stage,
            "upcomingIrrigation": upcoming_irrigation,
        }

    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/crop-plan/{crop_plan_id}")
def delete_crop_plan(crop_plan_id: str, db: Session = Depends(get_db)):
    """Delete a crop plan and all associated data from PostgreSQL (and Firebase if enabled)."""
    try:
        plan, user_id, crop_name = delete_plan_db(db, crop_plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        firebase_db = get_firestore()
        if firebase_db is not None:
            try:
                crop_plan_ref = firebase_db.collection("crop_plans").document(crop_plan_id)
                crop_plan_ref.delete()

                calendar_docs = firebase_db.collection("crop_calendar").where("cropPlanId", "==", crop_plan_id).stream()
                for doc in calendar_docs:
                    doc.reference.delete()

                schedule_docs = firebase_db.collection("irrigation_schedule").where("cropPlanId", "==", crop_plan_id).stream()
                for doc in schedule_docs:
                    doc.reference.delete()

                log_docs = firebase_db.collection("irrigation_logs").where("cropPlanId", "==", crop_plan_id).stream()
                for doc in log_docs:
                    doc.reference.delete()
                print(f"[INFO] Crop plan deleted from Firebase: {crop_plan_id}")
            except Exception as exc:  # pylint: disable=broad-except
                print(f"[WARNING] Failed to delete Firebase artifacts for {crop_plan_id}: {exc}")

        log_plan_deleted(crop_plan_id, user_id, crop_name)

        return {
            "success": True,
            "message": f"Crop plan '{crop_name}' deleted successfully",
            "deletedPlanId": crop_plan_id,
        }

    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] Failed to delete crop plan: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/all-logs")
def get_operation_logs():
    """Get all operation logs."""
    try:
        logs = get_all_logs()
        return logs
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/irrigation/logs/{crop_plan_id}")
def get_irrigation_logs(crop_plan_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch irrigation adjustment logs from PostgreSQL."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        plan = db.get(CropPlan, plan_uuid)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        logs = fetch_irrigation_logs(db, crop_plan_id, limit=limit)
        serialized = []
        for log in logs:
            status_text = (getattr(log, "status", None) or "completed").title()
            weather_adj = log.weather_adjustment or status_text
            if (log.weather_adjustment or "").lower().strip() == "no weather data":
                weather_adj = status_text

            serialized.append(
                {
                    "date": log.irrigation_date.isoformat() if getattr(log, "irrigation_date", None) else None,
                    "originalAmount": log.original_amount,
                    "adjustedAmount": log.adjusted_amount,
                    "reason": log.weather_adjustment,
                    "weatherAdjustment": weather_adj,
                    "result": weather_adj,
                    "status": status_text,
                    "autoTriggered": log.auto_triggered,
                    "plannedLiters": getattr(log, "planned_liters", None),
                    "actualLiters": getattr(log, "actual_liters", None),
                    "durationSeconds": getattr(log, "duration_seconds", None),
                    "weatherAdjustmentPercent": getattr(log, "weather_adjustment_percent", None),
                    "createdAt": log.created_at.isoformat() if getattr(log, "created_at", None) else None,
                    "executedAt": log.created_at.isoformat() if getattr(log, "created_at", None) else None,
                }
            )
        
        return {"logs": serialized}
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/irrigation/schedule/{crop_plan_id}")
def get_irrigation_schedule(
    crop_plan_id: str,
    limit: int = 7,
    moisture: float = None,
    refresh: bool = False,
    lat: float | None = None,
    lon: float | None = None,
    db: Session = Depends(get_db),
):
    """Fetch upcoming irrigation schedule. If refresh (or moisture) provided, regenerate using Weather API only (moisture ignored)."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        plan = db.get(CropPlan, plan_uuid)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        # Regenerate on demand using Weather API (moisture ignored). If today's entry is completed, start from tomorrow.
        if refresh or moisture is not None:
            weather_current = fetch_weather_data(lat or 18.45, lon or 73.87).get("current")
            stages = db.query(CropStage).filter(CropStage.crop_plan_id == plan_uuid).all()

            today_date = datetime.now(timezone.utc).date()
            today_start = datetime.combine(today_date, datetime.min.time(), tzinfo=timezone.utc)
            today_end = today_start + timedelta(days=1)
            entry_today = (
                db.query(IrrigationSchedule)
                .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
                .filter(IrrigationSchedule.date >= today_start)
                .filter(IrrigationSchedule.date < today_end)
                .order_by(IrrigationSchedule.date)
                .first()
            )
            start_date = today_date + timedelta(days=1) if entry_today and (entry_today.status or "").lower() == "completed" else today_date

            generate_irrigation_schedule(db, plan, stages, weather_current, None, start_date=start_date)

        today = datetime.now(timezone.utc)
        entries = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= today)
            .filter(IrrigationSchedule.status != "completed")
            .order_by(IrrigationSchedule.date)
            .limit(limit)
            .all()
        )
        serialized = [serialize_schedule(item) for item in entries]
        return serialized
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/calendar/{crop_plan_id}")
def get_calendar_events(crop_plan_id: str, db: Session = Depends(get_db)):
    """Return structured calendar data for stages, irrigation, health, and today marker."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        plan = db.get(CropPlan, plan_uuid)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        stages = (
            db.query(CropStage)
            .filter(CropStage.crop_plan_id == plan_uuid)
            .order_by(CropStage.start_date)
            .all()
        )
        schedule = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .order_by(IrrigationSchedule.date)
            .all()
        )

        stages_payload = [
            {
                "name": stage.stage,
                "start_date": stage.start_date.isoformat(),
                "end_date": stage.end_date.isoformat(),
            }
            for stage in stages
        ]

        irrigation_payload = [
            {
                "date": _as_date(item.date).isoformat() if _as_date(item.date) else None,
                "water_amount": item.water_amount_liters,
                "adjusted": item.auto_adjusted,
                "stage": item.stage,
                "status": item.status,
                "actual_liters": item.actual_liters,
                "executed_at": item.executed_at.isoformat() if item.executed_at else None,
                "weather_adjustment_percent": item.weather_adjustment_percent,
            }
            for item in schedule
        ]

        # Health score heuristic: start from 100 and subtract stresses
        skipped_irrigations = sum(1 for i in irrigation_payload if (i.get("status") or "").lower() in {"skipped", "missed"} or i.get("water_amount", 0) == 0)
        moisture_stress = 0  # placeholder until moisture sensor input is wired
        heat_stress = 0       # placeholder; could be derived from recent weather logs

        health_score = 100 - moisture_stress - heat_stress - (skipped_irrigations * 5)
        health_score = max(0, min(100, health_score))

        return {
            "stages": stages_payload,
            "irrigation": irrigation_payload,
            "today": datetime.now(timezone.utc).date().isoformat(),
            "crop_health_score": health_score,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/irrigation/trigger/{crop_plan_id}")
def trigger_irrigation(crop_plan_id: str, db: Session = Depends(get_db)):
    """Endpoint polled by Arduino to decide irrigation for today."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc).date()
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc))
            .order_by(IrrigationSchedule.date)
            .first()
        )
        if entry is None:
            return {"should_irrigate": False}

        return {
            "should_irrigate": True,
            "water_liters": entry.water_amount_liters,
            "method": entry.method,
            "schedule_id": str(entry.id),
            "date": entry.date.isoformat(),
        }
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/irrigation/next-command/{crop_plan_id}")
def next_command(crop_plan_id: str, lat: float | None = None, lon: float | None = None, db: Session = Depends(get_db)):
    """Arduino-friendly next action for irrigation with execution logging."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        _mark_missed_irrigations(db)

        start_today = _start_of_day(datetime.now(timezone.utc))
        end_today = start_today + timedelta(days=1)
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= start_today)
            .filter(IrrigationSchedule.date < end_today)
            .order_by(IrrigationSchedule.date)
            .first()
        )

        if entry is None or entry.water_amount_liters <= 0 or (entry.status not in {"pending", "adjusted", None}):
            return {
                "action": "SKIP",
                "liters": 0,
                "duration_seconds": 0,
                "reason": "No pending irrigation today",
            }

        weather = None
        if lat is not None and lon is not None:
            try:
                weather_resp = fetch_weather_data(lat, lon)
                weather = weather_resp.get("current") if isinstance(weather_resp, dict) else None
            except Exception:
                weather = None

        factor, reason, should_skip = _compute_weather_adjustment(weather)

        planned = entry.water_amount_liters or 0
        adjusted = round(planned * factor) if planned else 0
        weather_pct = round(((adjusted - planned) / planned) * 100, 2) if planned else 0
        now_ts = datetime.now(timezone.utc)

        if should_skip or adjusted <= 0:
            entry.status = "skipped"
            entry.actual_liters = 0
            entry.executed_at = now_ts
            entry.weather_adjustment_percent = -100 if planned else 0
            entry.auto_adjusted = True

            log_row = IrrigationLog(
                crop_plan_id=plan_uuid,
                irrigation_date=_as_date(entry.date),
                original_amount=planned,
                adjusted_amount=0,
                weather_adjustment=reason,
                auto_triggered=True,
                planned_liters=planned,
                actual_liters=0,
                duration_seconds=0,
                status="skipped",
                weather_adjustment_percent=entry.weather_adjustment_percent,
            )
            db.add(log_row)
            db.commit()
            return {
                "action": "SKIP",
                "liters": 0,
                "duration_seconds": 0,
                "reason": reason,
            }

        duration_seconds = int(max(0, adjusted) / 10)
        entry.status = "completed"
        entry.actual_liters = adjusted
        entry.executed_at = now_ts
        entry.weather_adjustment_percent = weather_pct
        entry.auto_adjusted = entry.auto_adjusted or factor != 1.0

        log_row = IrrigationLog(
            crop_plan_id=plan_uuid,
            irrigation_date=_as_date(entry.date),
            original_amount=planned,
            adjusted_amount=adjusted,
            weather_adjustment=reason,
            auto_triggered=True,
            planned_liters=planned,
            actual_liters=adjusted,
            duration_seconds=duration_seconds,
            status="completed",
            weather_adjustment_percent=weather_pct,
        )
        db.add(log_row)
        db.commit()

        return {
            "action": "WATER",
            "liters": adjusted,
            "duration_seconds": duration_seconds,
            "method": entry.method,
            "schedule_id": str(entry.id),
            "date": entry.date.isoformat(),
            "weather_adjustment_percent": weather_pct,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sensor/raindrop")
def register_raindrop(crop_plan_id: str, rain_mm: float, db: Session = Depends(get_db)):
    """
    Register raindrop sensor data for logging only. Weather API will drive decisions.
    POST /sensor/raindrop?crop_plan_id=xxx&rain_mm=6.5
    """
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= today_start)
            .filter(IrrigationSchedule.date < today_start + timedelta(days=1))
            .first()
        )
        
        if entry is None:
            return {"status": "no_schedule", "message": "No irrigation scheduled for today"}
        
        # For demo: do not alter schedule based on raindrop sensor; rely on Weather API rain.
        print(f"[SENSOR] Raindrop (logged only): {rain_mm}mm for plan {crop_plan_id}")
        return {"action": "LOGGED", "status": "accepted", "rain_mm": rain_mm}
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sensor/dht11")
def register_dht11(crop_plan_id: str, temperature: float, humidity: float, db: Session = Depends(get_db)):
    """
    Register DHT11 sensor data for logging only. Weather API will drive adjustments.
    POST /sensor/dht11?crop_plan_id=xxx&temperature=36.5&humidity=28
    """
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= today_start)
            .filter(IrrigationSchedule.date < today_start + timedelta(days=1))
            .first()
        )
        
        if entry is None:
            return {"status": "no_schedule", "message": "No irrigation scheduled for today"}

        # For demo: do not alter schedule based on DHT11; rely on Weather API temp/humidity.
        log_row = IrrigationLog(
            crop_plan_id=plan_uuid,
            irrigation_date=today,
            original_amount=entry.water_amount_liters or 0,
            adjusted_amount=entry.water_amount_liters or 0,
            weather_adjustment=f"DHT11 logged temp={temperature}°C humidity={humidity}% (no schedule change)",
            status="pending",
            weather_adjustment_percent=0,
        )
        db.add(log_row)
        db.commit()

        print(f"[SENSOR] DHT11 (logged only): temp={temperature}°C, humidity={humidity}% for plan {crop_plan_id}")
        return {
            "status": "logged",
            "temperature": temperature,
            "humidity": humidity,
            "message": "No schedule change; using Weather API for adjustments",
        }
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sensor/soil-moisture")
def register_soil_moisture(crop_plan_id: str, moisture_percent: float, db: Session = Depends(get_db)):
    """
    Log soil moisture sensor data only; irrigation decisions use Weather API.
    POST /sensor/soil-moisture?crop_plan_id=xxx&moisture_percent=45
    """
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= today_start)
            .filter(IrrigationSchedule.date < today_start + timedelta(days=1))
            .first()
        )
        
        if entry is None:
            return {"status": "no_schedule", "message": "No irrigation scheduled for today"}
        
        # Log only; do not alter schedule. Weather API drives irrigation.
        log_row = IrrigationLog(
            crop_plan_id=plan_uuid,
            irrigation_date=today,
            original_amount=entry.water_amount_liters or 0,
            adjusted_amount=entry.water_amount_liters or 0,
            weather_adjustment=f"Soil moisture logged: {moisture_percent}% (no schedule change)",
            status=entry.status or "pending",
            weather_adjustment_percent=0,
        )
        db.add(log_row)
        db.commit()

        print(f"[SENSOR] Soil Moisture (logged only): {moisture_percent}% for plan {crop_plan_id}")
        return {
            "status": "logged",
            "moisture_percent": moisture_percent,
            "message": "No schedule change; using Weather API",
        }
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.on_event("startup")
def warmup():
    try:
        # Warm minimal dependencies without blocking on local LLM
        get_firestore()  # Initialize Firebase
        db_gen = get_db()
        session = next(db_gen)
        try:
            _mark_missed_irrigations(session)
        finally:
            session.close()
            db_gen.close()
    except Exception:
        pass
