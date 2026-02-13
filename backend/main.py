import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from vectorstore.search import RAGSearch, build_context_text
from weather_engine.weather_service import fetch_weather_data
from weather_engine.weather_rules import build_weather_rules
from weather_engine.weather_ai import generate_weather_advice
from crop_engine.crop_planner import (
    generate_crop_stages,
    calculate_total_duration,
    generate_irrigation_schedule,
    get_current_stage,
    adjust_irrigation_for_weather,
)
from crop_engine.crop_insights import generate_crop_insight
from firebase_config import get_firestore, is_firebase_enabled
from logging_service import log_yield_input, log_plan_created, log_plan_deleted, log_irrigation_adjustment, get_all_logs
import uuid

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"

# In-memory storage for crop plans when Firebase is not configured
_memory_store = {
    "crop_plans": {},
    "crop_calendar": [],
    "irrigation_schedule": [],
}

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
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    context: str = ""


class WeatherRequest(BaseModel):
    lat: float
    lon: float
    include_ai: bool = True


class CropPlanRequest(BaseModel):
    userId: str
    cropName: str
    location: str
    soilType: str
    sowingDate: str
    irrigationMethod: str
    landSizeAcres: float
    expectedInvestment: Optional[float] = None
    waterSourceType: str


rag_search = RAGSearch()
chat_history = []


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
def create_crop_plan(req: CropPlanRequest):
    """Create new crop plan with calendar and irrigation schedule."""
    try:
        db = get_firestore()
        
        # Calculate total duration
        total_duration = calculate_total_duration(req.cropName)
        
        # Generate growth stages
        stages = generate_crop_stages(req.cropName, req.sowingDate)
        
        # Generate irrigation schedule
        irrigation_schedule = generate_irrigation_schedule(
            req.cropName,
            req.sowingDate,
            req.landSizeAcres,
            req.irrigationMethod,
            stages
        )
        
        # Generate crop plan ID
        crop_plan_id = str(uuid.uuid4())
        
        # Create crop plan document
        crop_plan_data = {
            "userId": req.userId,
            "cropName": req.cropName,
            "location": req.location,
            "soilType": req.soilType,
            "sowingDate": req.sowingDate,
            "growthDurationDays": total_duration,
            "irrigationMethod": req.irrigationMethod,
            "landSizeAcres": req.landSizeAcres,
            "expectedInvestment": req.expectedInvestment,
            "waterSourceType": req.waterSourceType,
            "createdAt": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Save to Firestore if available
        if db is not None:
            crop_plan_ref = db.collection("crop_plans").document()
            crop_plan_ref.set(crop_plan_data)
            crop_plan_id = crop_plan_ref.id
            
            # Save stages to crop_calendar
            for stage in stages:
                calendar_data = {
                    "cropPlanId": crop_plan_id,
                    **stage,
                }
                db.collection("crop_calendar").add(calendar_data)
            
            # Save irrigation schedule
            for schedule_item in irrigation_schedule:
                schedule_data = {
                    "cropPlanId": crop_plan_id,
                    **schedule_item,
                }
                db.collection("irrigation_schedule").add(schedule_data)
            
            print(f"[INFO] Crop plan saved to Firebase: {crop_plan_id}")
        else:
            # Save to memory store when Firebase not configured
            _memory_store["crop_plans"][crop_plan_id] = crop_plan_data
            
            for stage in stages:
                stage_data = {"cropPlanId": crop_plan_id, **stage}
                _memory_store["crop_calendar"].append(stage_data)
            
            for schedule_item in irrigation_schedule:
                schedule_data = {"cropPlanId": crop_plan_id, **schedule_item}
                _memory_store["irrigation_schedule"].append(schedule_data)
            
            print(f"[WARNING] Crop plan saved to memory (Firebase not configured): {crop_plan_id}")
        
        # Log the plan creation
        log_plan_created(crop_plan_id, req.userId, req.cropName, req.location)
        
        return {
            "success": True,
            "cropPlanId": crop_plan_id,
            "stages": stages,
            "irrigationSchedule": irrigation_schedule,
            "totalDurationDays": total_duration,
            "firebaseEnabled": db is not None,
        }
        
    except Exception as exc:
        print(f"[ERROR] Failed to create crop plan: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-plan/{crop_plan_id}")
def get_crop_plan(crop_plan_id: str):
    """Get crop plan details with calendar and schedule."""
    try:
        db = get_firestore()
        
        if db is None:
            # Use memory store
            crop_plan_data = _memory_store["crop_plans"].get(crop_plan_id)
            if not crop_plan_data:
                raise HTTPException(status_code=404, detail="Crop plan not found")
            
            calendar = [c for c in _memory_store["crop_calendar"] if c["cropPlanId"] == crop_plan_id]
            schedule = [s for s in _memory_store["irrigation_schedule"] if s["cropPlanId"] == crop_plan_id]
            current_stage = get_current_stage(calendar)
            
            return {
                "cropPlan": crop_plan_data,
                "calendar": calendar,
                "irrigationSchedule": schedule,
                "currentStage": current_stage,
            }
        
        # Get crop plan
        crop_plan_ref = db.collection("crop_plans").document(crop_plan_id)
        crop_plan_doc = crop_plan_ref.get()
        
        if not crop_plan_doc.exists:
            raise HTTPException(status_code=404, detail="Crop plan not found")
        
        crop_plan_data = crop_plan_doc.to_dict()
        
        # Get calendar
        calendar_docs = db.collection("crop_calendar").where("cropPlanId", "==", crop_plan_id).stream()
        calendar = [doc.to_dict() for doc in calendar_docs]
        
        # Get irrigation schedule
        schedule_docs = db.collection("irrigation_schedule").where("cropPlanId", "==", crop_plan_id).stream()
        schedule = [doc.to_dict() for doc in schedule_docs]
        
        # Get current stage
        current_stage = get_current_stage(calendar)
        
        return {
            "cropPlan": crop_plan_data,
            "calendar": calendar,
            "irrigationSchedule": schedule,
            "currentStage": current_stage,
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-plan/user/{user_id}")
def get_user_crop_plans(user_id: str):
    """Get all crop plans for a user."""
    try:
        db = get_firestore()
        
        if db is None:
            # Return plans from memory store
            plans = []
            for plan_id, plan_data in _memory_store["crop_plans"].items():
                if plan_data.get("userId") == user_id and plan_data.get("status") == "active":
                    plan_with_id = {"id": plan_id, **plan_data}
                    plans.append(plan_with_id)
            return {"plans": plans, "firebaseEnabled": False}
        
        plans_docs = db.collection("crop_plans").where("userId", "==", user_id).where("status", "==", "active").stream()
        plans = []
        
        for doc in plans_docs:
            plan_data = doc.to_dict()
            plan_data["id"] = doc.id
            plans.append(plan_data)
        
        return {"plans": plans, "firebaseEnabled": True}
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/irrigation/adjust")
def adjust_irrigation_schedule(crop_plan_id: str, lat: float, lon: float):
    """Adjust upcoming irrigation based on weather and log changes."""
    try:
        db = get_firestore()
        
        if db is None:
            raise HTTPException(
                status_code=503, 
                detail="Firebase not configured. Cannot adjust irrigation schedule."
            )
        
        # Get weather
        weather = fetch_weather_data(lat, lon)
        current_weather = weather["current"]
        
        # Get upcoming irrigation (next 7 days)
        today = datetime.now().isoformat()
        schedule_docs = (
            db.collection("irrigation_schedule")
            .where("cropPlanId", "==", crop_plan_id)
            .where("status", "==", "pending")
            .where("date", ">=", today)
            .limit(7)
            .stream()
        )
        
        adjustments = []
        
        for doc in schedule_docs:
            schedule_item = doc.to_dict()
            adjusted_amount, adjustment_reason = adjust_irrigation_for_weather(schedule_item, current_weather)
            
            # Update schedule
            doc.reference.update({"waterAmountLiters": adjusted_amount})
            
            # Log adjustment
            if adjustment_reason != "No adjustment needed":
                log_data = {
                    "cropPlanId": crop_plan_id,
                    "date": schedule_item["date"],
                    "originalAmount": schedule_item["waterAmountLiters"],
                    "adjustedAmount": adjusted_amount,
                    "weatherAdjustment": adjustment_reason,
                    "autoTriggered": True,
                    "createdAt": datetime.now(),
                }
                db.collection("irrigation_logs").add(log_data)
            
            adjustments.append({
                "date": schedule_item["date"],
                "originalAmount": schedule_item["waterAmountLiters"],
                "adjustedAmount": adjusted_amount,
                "reason": adjustment_reason,
            })
        
        return {"adjustments": adjustments}
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/crop-insight/{crop_plan_id}")
def get_crop_insight(crop_plan_id: str, lat: float, lon: float):
    """Generate AI-powered crop insight."""
    try:
        db = get_firestore()
        
        if db is None:
            raise HTTPException(
                status_code=503, 
                detail="Firebase not configured. Cannot retrieve crop plan for insights."
            )
        
        # Get crop plan
        crop_plan_ref = db.collection("crop_plans").document(crop_plan_id)
        crop_plan_doc = crop_plan_ref.get()
        
        if not crop_plan_doc.exists:
            raise HTTPException(status_code=404, detail="Crop plan not found")
        
        crop_plan_data = crop_plan_doc.to_dict()
        
        # Get calendar for current stage
        calendar_docs = db.collection("crop_calendar").where("cropPlanId", "==", crop_plan_id).stream()
        calendar = [doc.to_dict() for doc in calendar_docs]
        current_stage = get_current_stage(calendar)
        
        # Get upcoming irrigation
        today = datetime.now().isoformat()
        schedule_docs = (
            db.collection("irrigation_schedule")
            .where("cropPlanId", "==", crop_plan_id)
            .where("status", "==", "pending")
            .where("date", ">=", today)
            .limit(3)
            .stream()
        )
        upcoming_irrigation = [doc.to_dict() for doc in schedule_docs]
        
        # Get weather
        weather = fetch_weather_data(lat, lon)
        current_weather = weather["current"]
        
        # Generate insight
        insight = generate_crop_insight(
            crop_data={
                "crop_name": crop_plan_data.get("cropName"),
                "location": crop_plan_data.get("location"),
                "soil_type": crop_plan_data.get("soilType"),
                "sowing_date": crop_plan_data.get("sowingDate"),
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/crop-plan/{crop_plan_id}")
def delete_crop_plan(crop_plan_id: str):
    """Delete a crop plan and all associated data."""
    try:
        db = get_firestore()
        
        # Get plan first to get crop name for logging
        plan_data = None
        user_id = None
        crop_name = None
        
        if db is None:
            # Get from memory store
            plan_data = _memory_store["crop_plans"].get(crop_plan_id)
            if not plan_data:
                raise HTTPException(status_code=404, detail="Crop plan not found")
            
            user_id = plan_data.get("userId")
            crop_name = plan_data.get("cropName")
            
            # Delete from memory store
            del _memory_store["crop_plans"][crop_plan_id]
            _memory_store["crop_calendar"] = [c for c in _memory_store["crop_calendar"] if c.get("cropPlanId") != crop_plan_id]
            _memory_store["irrigation_schedule"] = [s for s in _memory_store["irrigation_schedule"] if s.get("cropPlanId") != crop_plan_id]
            
            print(f"[INFO] Crop plan deleted from memory: {crop_plan_id}")
        else:
            # Get plan from Firebase
            crop_plan_ref = db.collection("crop_plans").document(crop_plan_id)
            crop_plan_doc = crop_plan_ref.get()
            
            if not crop_plan_doc.exists:
                raise HTTPException(status_code=404, detail="Crop plan not found")
            
            plan_data = crop_plan_doc.to_dict()
            user_id = plan_data.get("userId")
            crop_name = plan_data.get("cropName")
            
            # Delete from Firebase
            crop_plan_ref.delete()
            
            # Delete related calendar entries
            calendar_docs = db.collection("crop_calendar").where("cropPlanId", "==", crop_plan_id).stream()
            for doc in calendar_docs:
                doc.reference.delete()
            
            # Delete related irrigation schedule
            schedule_docs = db.collection("irrigation_schedule").where("cropPlanId", "==", crop_plan_id).stream()
            for doc in schedule_docs:
                doc.reference.delete()
            
            # Delete related irrigation logs
            log_docs = db.collection("irrigation_logs").where("cropPlanId", "==", crop_plan_id).stream()
            for doc in log_docs:
                doc.reference.delete()
            
            print(f"[INFO] Crop plan deleted from Firebase: {crop_plan_id}")
        
        # Log the deletion
        log_plan_deleted(crop_plan_id, user_id, crop_name)
        
        return {
            "success": True,
            "message": f"Crop plan '{crop_name}' deleted successfully",
            "deletedPlanId": crop_plan_id,
        }
        
    except HTTPException:
        raise
    except Exception as exc:
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


@app.on_event("startup")
def warmup():
    try:
        generate_reply("hello")
        get_firestore()  # Initialize Firebase
    except Exception:
        pass
