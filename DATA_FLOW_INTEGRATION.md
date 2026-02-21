# 🌾 Smart Farming Assistant - Data Flow & Integration Guide

---

## 📊 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SMART FARMING ASSISTANT                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────┐  ┌──────────────────────────────┐
│          FRONTEND (React 19)              │  │    BACKEND (FastAPI)         │
│          localhost:5173                   │  │    localhost:8000            │
│                                           │  │                              │
│  ┌─────────────────────────────────────┐  │  │  ┌──────────────────────────┐
│  │         Pages (8 Total)             │  │  │  │  Endpoints (12 Total)    │
│  │ ┌─────────────────────────────────┐ │  │  │  │ ┌────────────────────────┐
│  │ │ Home / ── Feature Cards         │ │  │  │  │ │ GET /health            │
│  │ │ Yield Input /yield              │ │◄─┼──┼─►│ │ POST /chat ⭐          │
│  │ │ Irrigation /irrigation          │ │  │  │  │ │ POST /crop-plans       │
│  │ │ Chatbot /chatbot ⭐             │ │  │  │  │ │ GET /crop-plans/{id}   │
│  │ │ Dashboard /dashboard            │ │  │  │  │ │ PUT /crop-plans/{id}   │
│  │ │ Crop Mgmt /crop-management      │ │  │  │  │ │ DELETE /crop-plans/{id}│
│  │ │ Calendar /calendar              │ │  │  │  │ │ GET /weather           │
│  │ │ Weather /weather                │ │  │  │  │ │ POST /irrigation/adjust│
│  │ └─────────────────────────────────┘ │  │  │  │ │ GET /dashboard/{id}    │
│  │ ⭐ Most Used: Chatbot, Dashboard     │  │  │  │ └────────────────────────┘
│  └─────────────────────────────────────┘  │  │  └──────────────────────────┘
│                                            │  │
│  ┌─────────────────────────────────────┐  │  │  ┌──────────────────────────┐
│  │  Services & Hooks                   │  │  │  │  Core Engines            │
│  │ ├─ weatherService.js                │  │  │  │ ├─ crop_engine/          │
│  │ ├─ locationService.js               │  │  │  │ ├─ weather_engine/       │
│  │ ├─ useIrrigationData (hook)         │  │  │  │ ├─ irrigation_engine/    │
│  │ └─ Firebase (auth + realtime DB)    │  │  │  │ └─ vectorstore/ (RAG)    │
│  └─────────────────────────────────────┘  │  │  └──────────────────────────┘
│                                            │  │
│  ┌─────────────────────────────────────┐  │  │  ┌──────────────────────────┐
│  │  State Management                   │  │  │  │  Database (PostgreSQL)   │
│  │ ├─ Context API (CropContext)        │  │  │  │ ├─ crop_plans table      │
│  │ ├─ useState (local components)      │  │  │  │ ├─ crop_stages table     │
│  │ └─ Firebase Realtime Sync           │  │  │  │ ├─ irrigation_schedule   │
│  └─────────────────────────────────────┘  │  │  │ ├─ irrigation_logs       │
│                                            │  │  │ └─ weather_logs table    │
└────────────────────────────────────────────┘  └──────────────────────────────┘
         HTTP JSON                                    HTTP JSON
         (Fetch API)                                (Uvicorn ASGI)
```

---

## 🔄 Request/Response Flow Examples

### Example 1: User Sends Chat Message

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO: User types crop question in Chatbot page                          │
└─────────────────────────────────────────────────────────────────────────────┘

FRONTEND (Chatbot.jsx)
├── User types: "How much water for wheat?"
├── Clicks Send button
├── handleSendMessage() function triggered
│   ├── Create message object
│   │   {
│   │     "message": "How much water for wheat?",
│   │     "context": "Crop: Wheat, Location: Pune"
│   │   }
│   ├── POST to http://localhost:8000/chat
│   ├── Show loading indicator
│   └── Add user message to messages array

NETWORK
├── HTTP POST request
├── Content-Type: application/json
├── Body: {...message object...}
└── Destination: http://localhost:8000/chat

BACKEND (main.py)
├── @app.post("/chat")
├── Receive ChatRequest
│   {
│     "message": "How much water for wheat?",
│     "context": "Crop: Wheat, Location: Pune"
│   }
├── Validate with Pydantic (schemas.py)
├── Call RAGSearch.search(message)
│   ├── Embed the question into vector space
│   ├── Search vectorstore for similar documents
│   ├── Retrieve top 3 agriculture knowledge documents
│   └── Build context_text from retrieved docs
├── Prepare system prompt (farming expert persona)
├── Call LLM (Hugging Face or Ollama)
│   ├── Input:
│   │   - System prompt
│   │   - Retrieved context
│   │   - Chat history
│   │   - User message
│   └── Output: AI-generated farming advice
├── Log interaction to logging_service
├── Return response:
│   {
│     "response": "For wheat at this growth stage...",
│     "source": "agriculture_kb",
│     "used_context": true
│   }

NETWORK
├── HTTP 200 response
├── Content-Type: application/json
├── Body: {...response object...}
└── Source: http://localhost:8000/chat

FRONTEND (Chatbot.jsx)
├── Receive response
├── Parse JSON
├── Add bot message to messages array
├── Hide loading indicator
├── useEffect hook triggers
│   └── Auto-scroll chat to bottom
└── User sees: "For wheat at this growth stage..."
```

---

### Example 2: Create Crop Plan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO: User submits form on Irrigation/Crop Management page              │
└─────────────────────────────────────────────────────────────────────────────┘

FRONTEND (CropManagement.jsx or Irrigation.jsx)
├── User fills form:
│   ├── Crop: "Wheat"
│   ├── Location: "Pune"
│   ├── Soil Type: "Loam"
│   ├── Sowing Date: "2026-03-01"
│   ├── Irrigation Method: "Drip"
│   ├── Land Size: 5 acres
│   └── Investment: 50000
├── handleSubmit() called
├── Create CropPlanRequest object:
│   {
│     "userId": "user_123",
│     "cropName": "Wheat",
│     "location": "Pune",
│     "soilType": "Loam",
│     "sowingDate": "2026-03-01",
│     "irrigationMethod": "Drip",
│     "landSizeAcres": 5,
│     "expectedInvestment": 50000,
│     "waterSourceType": "Borewell"
│   }
├── POST to http://localhost:8000/crop-plans
└── Show: "Creating your crop plan..."

NETWORK
├── HTTP POST
├── Location: http://localhost:8000/crop-plans
└── Body: CropPlanRequest JSON

BACKEND (main.py)
├── @app.post("/crop-plans")
├── Receive & validate CropPlanRequest
├── Get database session
├── Call create_crop_plan() from crop_service.py
│   │
│   ├── Calculate total duration from crop_data.py
│   │   └── CROP_STAGES["Wheat"] = 130 days
│   │
│   ├── Generate crop stages (crop_planner.py)
│   │   ├── Seedling: Mar 1 - Mar 20 (20 days)
│   │   ├── Vegetative: Mar 20 - Apr 29 (40 days)
│   │   ├── Flowering: Apr 29 - May 19 (20 days)
│   │   ├── Grain Filling: May 19 - Jun 8 (20 days)
│   │   └── Maturity: Jun 8 - Jun 30 (22 days)
│   │
│   ├── Generate irrigation schedule (crop_planner.py)
│   │   ├── For each stage:
│   │   │   ├── Get WATER_REQUIREMENTS[crop][stage]
│   │   │   ├── Calculate water = base * land_size * soil_adjustment
│   │   │   ├── Create schedule items every N days
│   │   │   └── Default: 1000-2000 liters/acre per irrigation
│   │   │
│   │   └── Total schedule: ~25-30 irrigation events across 130 days
│   │
│   └── Save to database:
│       ├── INSERT into crop_plans table
│       │   └── Returns: plan_id (UUID)
│       ├── INSERT into crop_stages table (5 records)
│       └── INSERT into irrigation_schedule table (25 records)
│
├── Serialize response with crop_service.serialize_plan()
│   {
│     "id": "550e8400-e29b-41d4...",
│     "userId": "user_123",
│     "cropName": "Wheat",
│     "growthDurationDays": 130,
│     "stages": [
│       {
│         "stage": "Seedling",
│         "startDate": "2026-03-01",
│         "endDate": "2026-03-20",
│         "durationDays": 20,
│         "recommendedIrrigationFrequencyDays": 3
│       },
│       ...more stages...
│     ],
│     "irrigationSchedule": [
│       {
│         "date": "2026-03-04",
│         "stage": "Seedling",
│         "waterAmountLiters": 1200,
│         "method": "Drip",
│         "status": "pending"
│       },
│       ...more schedules...
│     ]
│   }

NETWORK
├── HTTP 200 Created
├── Content-Type: application/json
└── Body: Full plan with all stages and schedules

FRONTEND (CropManagement.jsx)
├── Receive response
├── Store plan in state/context
├── Update CropContext with new plan
├── Re-render component
├── Show success message: "Crop plan created!"
├── Display irrigation timeline
├── Update Dashboard to show new crop
└── Navigate to crop details page
```

---

### Example 3: Get Real-time Weather & Adjust Irrigation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO: Dashboard loads, fetches weather, system auto-adjusts irrigation   │
└─────────────────────────────────────────────────────────────────────────────┘

FRONTEND (Dashboard.jsx)
├── useEffect hooks on component mount
├── Call fetchWeatherData(lat, lon)
│   ├── Get user's location via geolocation API
│   ├── POST to http://localhost:8000/weather
│   │   {
│   │     "lat": 18.5204,
│   │     "lon": 73.8567
│   │   }
│   └── Receive weather response
│
└── Display:
    ├── Current: 28°C, 65% humidity
    ├── Forecast: 7 days
    └── Alerts: "⚠️ Rain expected tomorrow"

BACKEND (main.py - /weather endpoint)
├── Receive WeatherRequest (lat, lon)
├── Call weather_service.fetch_weather_data(lat, lon)
│   │
│   ├── Make API call to OpenWeather
│   │   ├── API: https://api.openweathermap.org/data/3.0/onecall
│   │   └── Params: lat, lon, api_key
│   │
│   ├── Parse response:
│   │   {
│   │     "current": {
│   │       "temp": 28,
│   │       "humidity": 65,
│   │       "wind_speed": 12,
│   │       "rain": 0
│   │     },
│   │     "hourly": [...24 hours...],
│   │     "daily": [
│   │       {
│   │         "day": "Sat",
│   │         "min": 22,
│   │         "max": 32,
│   │         "rain_chance": 85,  ← Heavy rain tomorrow!
│   │         "condition": "Rain"
│   │       },
│   │       ...7 days...
│   │     ]
│   │   }
│   │
│   └── Store in WeatherLog table
│
├── Call generate_weather_advice() from weather_ai.py
│   ├── Analyze forecast
│   ├── Generate farmer-friendly advice
│   └── Return: "Skip irrigation due to heavy rain forecast"
│
└── Return to frontend:
    {
      "current": {...},
      "hourly": [...],
      "daily": [...],
      "advice": "Skip irrigation due to heavy rain forecast"
    }

BACKEND (Automatic: post weather fetch)
├── System triggers crop_service.adjust_schedule_for_weather()
├── For each active crop plan:
│   ├── Get next irrigation scheduled for tomorrow
│   ├── Check weather forecast for that day
│   ├── If rain_chance > 60%:
│   │   ├── Update irrigation_schedule.status = "skipped"
│   │   ├── Calculate adjustment:
│   │   │   - Original: 1500 liters
│   │   │   - Rain expected: 50mm
│   │   │   - Adjustment: -100% (skip entirely)
│   │   ├── Log adjustment to IrrigationLog
│   │   └── If Firebase enabled, send real-time update
│   │
│   └── Else: Keep original schedule
│
└── Result: Irrigation automatically skipped, farmer notified

FRONTEND (Realtime Update)
├── Firebase listener triggers (if FB enabled)
├── Receive updated schedule via WebSocket
├── Update Dashboard to show:
│   └── "⚠️ Tomorrow's irrigation skipped due to rain forecast"
├── Show irrigation timeline with crossed-out event
└── No manual intervention needed!
```

---

## 🔗 API Endpoints Breakdown

### Chat Endpoint
**POST** `/chat`
- **Purpose**: AI-powered farming assistant
- **Request**:
  ```json
  {
    "message": "How much water for wheat?",
    "context": "Location: Pune, Crop: Wheat, Stage: Seedling"
  }
  ```
- **Process**:
  1. RAG search for relevant documents
  2. Build LLM prompt with context
  3. Generate AI response
  4. Log conversation
- **Response**:
  ```json
  {
    "response": "For wheat seedling stage...",
    "source": "agriculture_kb"
  }
  ```
- **Used By**: Chatbot page

---

### Crop Plans Endpoints
**POST** `/crop-plans`
- **Purpose**: Create new crop plan
- **Input**: CropPlanRequest (crop, location, date, etc.)
- **Output**: Complete plan with stages & schedules
- **Database**: Saves to crop_plans, crop_stages, irrigation_schedule

**GET** `/crop-plans/{userId}`
- **Purpose**: List all user's crop plans
- **Output**: Array of plans with summaries

**GET** `/crop-plans/{planId}`
- **Purpose**: Get single plan with all details
- **Output**: Full plan object

**PUT** `/crop-plans/{planId}`
- **Purpose**: Update existing plan
- **Recalculates**: Stages and schedules

**DELETE** `/crop-plans/{planId}`
- **Purpose**: Remove plan
- **Cascade**: Deletes related stages, schedules, logs

---

### Weather & Irrigation Endpoints
**GET** `/weather?lat=X&lon=Y`
- **Purpose**: Fetch weather data
- **Data Source**: OpenWeather API
- **Features**: 7-day + hourly forecast + AI advice

**POST** `/irrigation/adjust`
- **Purpose**: Adjust schedule based on weather
- **Logic**: Reduce water if rain expected, increase if dry
- **Logging**: Records all adjustments

**GET** `/dashboard/{userId}`
- **Purpose**: Fetch metrics for dashboard
- **Data**:
  - Current crops & stages
  - Soil metrics
  - Weather conditions
  - Irrigation status
  - Yield statistics

---

## 📡 Real-time Features

### Firebase Integration (Optional)
- **Real-time Database**: Crop status updates
- **Cloud Functions**: Trigger irrigations automatically
- **Cloud Messaging**: Send alerts to farmer
- **Examples**:
  - "Rain detected, irrigation paused"
  - "Stage 2 complete, moving to flowering"
  - "Soil moisture low, time to irrigate"

### WebSocket Updates (Future)
- Live sensor data
- Irrigation commands
- Weather alerts

---

## 🔄 Data Persistence

### Frontend
- **Local**: useState, useContext
- **Session**: Browser session storage
- **Persistent**: Firebase Realtime DB
- **API Cache**: Fetch on demand

### Backend
- **Active**: In-memory cache (LRU)
- **Persistent**: PostgreSQL tables
- **Audit Trail**: All changes logged
- **Backup**: Firebase Cloud Storage

---

## 🔐 Authentication Flow

```
Frontend
  ├── Firebase Auth (email/password)
  ├── Get JWT token from Firebase
  └── Include token in API headers

Backend
  ├── Every API call includes: Authorization: Bearer {token}
  ├── Verify token signature
  ├── Extract user_id from token
  └── Scope database queries to user_id only
```

---

## 🚀 Deployment Architecture

### Frontend
```
npm run build
  ↓
Creates dist/ folder
  ↓
Deploy to:
  ├── Vercel (recommended)
  ├── Netlify
  ├── GitHub Pages
  ├── AWS S3 + CloudFront
  └── Any static hosting
```

### Backend
```
Python + FastAPI
  ↓
Deploy to:
  ├── Render (free tier)
  ├── Railway
  ├── Heroku
  ├── AWS EC2 + Gunicorn
  ├── Google Cloud Run
  └── Docker container
```

---

## 📊 Performance Metrics

| Operation | Time | Count |
|-----------|------|-------|
| Frontend Build | 6.28s | 1,967 modules |
| Chat Response | <2s | RAG search + LLM |
| Get Crop Plans | <100ms | SQLAlchemy query |
| Weather Update | ~1s | External API |
| Create Plan | ~500ms | DB write + relations |

---

## ✅ Integration Checklist

- [x] Frontend builds successfully
- [x] Backend imports all modules
- [x] Database migrations ready
- [x] API endpoints defined
- [x] Pydantic validation working
- [x] CORS configured for localhost:5173
- [x] Firebase SDK integrated
- [x] Weather API ready (needs key)
- [x] RAG vectorstore ready
- [x] Logging service ready

---

**Documentation Created**: February 21, 2026
