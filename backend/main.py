import os
import uuid
import requests
from datetime import datetime, timezone, date
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from vectorstore.search import RAGSearch, build_context_text
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
from models import CropStage, IrrigationSchedule, CropPlan
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

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"

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
- Never exceed 8 lines unless the question is complex

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
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
    return (
        f"{SYSTEM_PROMPT}\n----------------\nRetrieved context from documents:\n{context_text}\n----------------\n"
        f"{history_block}User question:\n{user_message}"
    ).strip()


def generate_reply(user_message: str) -> str:
    """Generate reply using local Ollama Mistral model."""
    try:
        chunks = rag_search.retrieve_context(user_message, top_k=5)
        context_text = build_context_text(chunks)
    except Exception:
        context_text = ""

    history_text = _format_history()

    prompt = _build_prompt(user_message, context_text, history_text)
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
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
            error_json = response.json()
            error_message = error_json.get("error") or response.text
        except ValueError:
            error_message = response.text
        return f"Model error: {error_message}"

    try:
        data = response.json()
    except ValueError:
        return "Model error: Invalid JSON response"

    generated_text = data.get("response", "") if isinstance(data, dict) else ""
    if not generated_text:
        return "Model error: Empty response from model"

    reply = generated_text.strip()

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": reply})

    return reply


@app.post("/chat")
def chat(req: ChatRequest):
    """Chat endpoint for agriculture advice"""
    reply = generate_reply(req.message)
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
def get_irrigation_logs(crop_plan_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Fetch irrigation adjustment logs from PostgreSQL."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        plan = db.get(CropPlan, plan_uuid)
        if plan is None:
            raise HTTPException(status_code=404, detail="Crop plan not found")

        logs = fetch_irrigation_logs(db, crop_plan_id, limit=limit)
        serialized = [
            {
                "date": log.date.isoformat() if log.date else None,
                "originalAmount": log.original_amount,
                "adjustedAmount": log.adjusted_amount,
                "reason": log.weather_adjustment,
                "autoTriggered": log.auto_triggered,
                "createdAt": log.created_at.isoformat() if getattr(log, "created_at", None) else None,
            }
            for log in logs
        ]
        return {"logs": serialized}
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/irrigation/schedule/{crop_plan_id}")
def get_irrigation_schedule(crop_plan_id: str, limit: int = 7, db: Session = Depends(get_db)):
    """Fetch upcoming irrigation schedule entries."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc)
        entries = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= today)
            .order_by(IrrigationSchedule.date)
            .limit(limit)
            .all()
        )
        serialized = [
            {
                "date": item.date.isoformat(),
                "stage": item.stage,
                "water": item.water_amount_liters,
                "status": item.status,
                "autoAdjusted": item.auto_adjusted,
            }
            for item in entries
        ]
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
                "date": item.date.isoformat(),
                "water_amount": item.water_amount_liters,
                "adjusted": item.auto_adjusted,
                "stage": item.stage,
                "status": item.status,
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
def next_command(crop_plan_id: str, db: Session = Depends(get_db)):
    """Arduino-friendly next action for irrigation."""
    try:
        plan_uuid = uuid.UUID(crop_plan_id)
        today = datetime.now(timezone.utc).date()
        start_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        entry = (
            db.query(IrrigationSchedule)
            .filter(IrrigationSchedule.crop_plan_id == plan_uuid)
            .filter(IrrigationSchedule.date >= start_today)
            .order_by(IrrigationSchedule.date)
            .first()
        )
        if entry is None or entry.water_amount_liters <= 0 or entry.status not in {"pending", None}:
            return {
                "action": "SKIP",
                "liters": 0,
                "duration_seconds": 0,
            }

        liters = entry.water_amount_liters
        duration_seconds = int(max(0, liters) / 10)  # simple flow heuristic
        return {
            "action": "WATER",
            "liters": liters,
            "duration_seconds": duration_seconds,
            "method": entry.method,
            "schedule_id": str(entry.id),
            "date": entry.date.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc))


@app.on_event("startup")
def warmup():
    try:
        # Warm minimal dependencies without blocking on local LLM
        get_firestore()  # Initialize Firebase
    except Exception:
        pass
