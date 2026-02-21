# 🌾 Smart Farming Assistant - COMPLETE SETUP GUIDE

## ✅ Project Overview

A full-stack web application for smart agriculture with:
- **Frontend**: React + Vite + React Router (8 pages)
- **Backend**: FastAPI + PostgreSQL + Firebase
- **Features**: Crop planning, irrigation scheduling, weather analysis, AI chatbot
- **Database**: PostgreSQL for persistence, Firebase for optional mirroring

---

## 📋 STEP-BY-STEP SETUP

### **PHASE 1: Environment & Database Setup**

#### Step 1: PostgreSQL Installation & Setup
```bash
# 1. Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Linux: sudo apt install postgresql postgresql-contrib
# Mac: brew install postgresql

# 2. Start PostgreSQL Service
# Windows (PowerShell admin): 
net start PostgreSQL15

# Linux/Mac:
sudo service postgresql start

# 3. Connect to PostgreSQL
psql -U postgres

# 4. Create the database and user (in psql)
CREATE DATABASE smart_irrigation;
CREATE USER agri_user WITH PASSWORD 'farming123';
ALTER ROLE agri_user SET client_encoding TO 'utf8';
ALTER ROLE agri_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE agri_user SET default_transaction_deferrable TO on;
ALTER ROLE agri_user SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE smart_irrigation TO agri_user;
\q
```

**Or use the existing credentials** (default in .env):
```
Username: postgres
Password: NIKKKHIL001
Database: smart_irrigation
```

#### Step 2: Backend Environment Configuration
```bash
cd backend

# .env file is already created. Verify/update:
cat .env

# Key settings to verify:
# DATABASE_URL=postgresql+psycopg2://postgres:NIKKKHIL001@localhost:5432/smart_irrigation
# OPENWEATHER_API_KEY=your_api_key (get from openweathermap.org)
# HF_API_KEY=your_huggingface_key (get from huggingface.co)
```

#### Step 3: Initialize Database Schema
```bash
cd backend

# Install dependencies first
pip install -r requirements.txt

# Run database initialization
python init_db.py

# Expected output:
# ✅ Database connection successful!
# ✅ Tables created successfully!
# ✅ DATABASE INITIALIZATION COMPLETE
```

---

### **PHASE 2: Backend Server Setup**

#### Step 4: Install Backend Dependencies
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate:
# Windows:
venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Verify Ollama (Local LLM)
```bash
# Install Ollama from https://ollama.ai
# Windows: Download and run installer
# Linux: curl https://ollama.ai/install.sh | sh
# Mac: Download from ollama.ai

# Start Ollama service
ollama serve

# In another terminal, pull Mistral model
ollama pull mistral:latest

# Verify it's loaded
ollama list
# Expected: mistral    latest    ...
```

#### Step 6: Start FastAPI Backend
```bash
cd backend

# Start server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

#### Step 7: Verify Backend Health
```bash
# In browser or curl:
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"ok"}

# View API docs:
http://127.0.0.1:8000/docs
```

---

### **PHASE 3: Frontend Setup**

#### Step 8: Install Frontend Dependencies
```bash
# From project root (not backend/)
cd ..

npm install

# Verify installation:
npm list react react-router-dom firebase

# Expected: All packages listed with versions
```

#### Step 9: Verify Frontend Environment
```bash
# Check .env file exists
cat .env

# Should contain:
# VITE_API_BASE_URL=http://localhost:8000
```

#### Step 10: Start Frontend Dev Server
```bash
# From project root
npm run dev

# Expected output:
#   VITE v5.x.x  ready in xxx ms
#   ➜  Local:   http://localhost:5173/
#   ➜  press h to show help
```

#### Step 11: Verify Frontend is Running
```bash
# Open browser to:
http://localhost:5173/

# Should see:
# - Home page with "Smart Farming Assistant" title
# - Navigation menu working
# - All pages accessible
```

---

## 🧪 TESTING THE COMPLETE SYSTEM

### Test 1: Create a Crop Plan
1. Frontend: Click "Yield Input" → Fill form → Submit
   - Crop: Rice
   - Sowing Date: Today
   - Location: Pune
   - Soil Type: Black
   - Expected Investment: 5000
   - Water Source: Borewell
   - Irrigation: Drip

2. Verify in Backend Logs:
   ```
   [INFO] New crop plan created: ...
   ✅ Should see crop plan ID returned
   ```

3. Verify in Database:
   ```bash
   psql -U postgres -d smart_irrigation -c "SELECT id, crop_name, location FROM crop_plans LIMIT 1;"
   ```

### Test 2: View Crop Management
1. Frontend: Go to "Crop Management"
2. Should see the created crop plan
3. Click "View Irrigation Schedule"

### Test 3: Check Irrigation Schedule
1. Verify irrigation data loads
2. Check next 7 days of irrigation times
3. Expected data in backend logs: `[INFO] Fetching irrigation schedule...`

### Test 4: Test Chatbot
1. Frontend: Go to "Chatbot"
2. Type: "How much water does rice need?"
3. Backend should respond with farming advice
4. Check backend logs:
   ```
   [INFO] Chat request: "How much water does rice need?"
   [INFO] Generated reply using Mistral
   ```

### Test 5: Weather & Dashboard
1. Go to "Weather Forecast"
2. Should show current location weather
3. Go to "Dashboard" - view metrics
4. All data should load without errors

---

## 🔧 TROUBLESHOOTING

### Issue: "Cannot connect to database"
```bash
# Check PostgreSQL is running:
# Windows: Check Services (services.msc) for PostgreSQL15 running
# Linux: sudo service postgresql status

# Check credentials in backend/.env
# Verify DATABASE_URL is correct:
DATABASE_URL=postgresql+psycopg2://postgres:NIKKKHIL001@localhost:5432/smart_irrigation

# Test connection manually:
psql -U postgres -h localhost -d smart_irrigation
```

### Issue: "Backend not responding" / "Cannot reach http://127.0.0.1:8000"
```bash
# Check FastAPI is running:
ps aux | grep uvicorn  # Linux/Mac
tasklist | grep python  # Windows

# Restart backend:
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Check port 8000 is not in use:
# Windows: netstat -ano | findstr :8000
# Linux: sudo lsof -i :8000
```

### Issue: "Ollama model not found"
```bash
# Check Ollama is running:
ollama list

# If not running:
ollama serve  # Start in separate terminal

# Pull Mistral:
ollama pull mistral:latest

# Verify:
curl http://localhost:11434/api/tags
```

### Issue: "Frontend shows 'Connection error'"
```bash
# Check .env file in project root:
cat .env

# Should have:
VITE_API_BASE_URL=http://localhost:8000

# Restart frontend:
npm run dev

# Clear browser cache: Ctrl+Shift+Delete / Cmd+Shift+Delete
# Hard refresh: Ctrl+Shift+R / Cmd+Shift+R
```

### Issue: "Firebase errors but system won't work"
```bash
# Firebase is OPTIONAL - system works without it
# If Firebase errors appear, just ignore them
# All data persists in PostgreSQL

# To disable Firebase errors in backend logs:
# Edit backend/firebase_config.py line 17 and remove the warning
```

### Issue: "tables don't exist"
```bash
# Run initialization again:
cd backend
python init_db.py

# If still fails, manually create:
psql -U postgres -d smart_irrigation << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
EOF

# Then re-run init:
python init_db.py
```

---

## 📊 DATABASE SCHEMA

### Tables Created:
```sql
crop_plans              -- Store crop information & metadata
crop_stages            -- Growth stages (sowing, vegetative, flowering, etc.)
irrigation_schedule    -- Planned irrigation events
irrigation_logs        -- Actual irrigation executed
weather_logs           -- Weather data snapshots
```

### View Existing Data:
```bash
# Connect to database
psql -U postgres -d smart_irrigation

# List all crop plans:
SELECT id, crop_name, location, sowing_date FROM crop_plans;

# List irrigation schedules:
SELECT * FROM irrigation_schedule LIMIT 5;

# List irrigation logs:
SELECT * FROM irrigation_logs LIMIT 5;

# Exit:
\q
```

---

## 🚀 RUNNING THE COMPLETE SYSTEM

### Terminal Setup (4 terminals recommended):

**Terminal 1: PostgreSQL** (if not running as service)
```bash
# Optional if PostgreSQL is running as service
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start
```

**Terminal 2: Ollama Server**
```bash
ollama serve
# Stays running in background
```

**Terminal 3: FastAPI Backend**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
# Keep running - shows debug logs
```

**Terminal 4: React Frontend**
```bash
cd ..
npm run dev
# Keep running - shows build logs
```

### Shutdown:
- Press Ctrl+C in each terminal
- Or close terminals (services will stop gracefully)

---

## 📱 ACCESSING THE APPLICATION

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:5173 | Main web app |
| **Backend API** | http://127.0.0.1:8000 | API server |
| **API Docs** | http://127.0.0.1:8000/docs | Swagger docs |
| **Health Check** | http://127.0.0.1:8000/health | Server status |
| **Ollama** | http://localhost:11434 | Local LLM (admin only) |

---

## 🎯 FEATURE WALKTHROUGH

### 1. Home Page (`/`)
- Landing page with hero section
- Feature cards with descriptions
- Navigation to all main features

### 2. Yield Input (`/yield`)
- Form to create crop plans
- Collects: crop, location, soil, dates, investment
- Stores in PostgreSQL
- Displays success confirmation

### 3. Crop Management (`/crop-management`)
- Lists all created crop plans
- Shows crop status, health, weather risks
- Options to view details, delete, or manage irrigation

### 4. Crop Calendar (`/calendar`)
- Visual timeline of crop growth stages
- Color-coded stages
- Irrigation event markers
- Estimated harvest date

### 5. Irrigation (`/irrigation`)
- Displays upcoming irrigation schedule
- Weather-based adjustments shown
- Soil moisture data (if connected to sensors)
- Irrigation logs and history

### 6. Weather Forecast (`/weather`)
- Current location weather
- 7-day forecast
- Weather rules for farming
- AI-powered recommendations

### 7. Chatbot (`/chatbot`)
- Ask farming questions
- Responses from local Mistral model
- Voice input support (browser-dependent)
- Chat history maintained

### 8. Dashboard (`/dashboard`)
- Real-time farm metrics
- Soil pH, temperature, moisture
- Humidity and pressure
- Crop health status

---

## 📚 IMPORTANT FILES TO KNOW

### Frontend
- **src/App.jsx** - Main router, all pages configured
- **src/context/CropContext.jsx** - Global state for crops
- **src/firebase.js** - Firebase configuration
- **src/pages/** - All 8 page components

### Backend
- **backend/main.py** - All API endpoints (~1000 lines)
- **backend/models.py** - SQLAlchemy database models
- **backend/database.py** - PostgreSQL connection
- **backend/firebase_config.py** - Optional Firebase
- **backend/crop_engine/** - Crop planning logic
- **backend/irrigation_engine/** - Irrigation calculations
- **backend/weather_engine/** - Weather API integration

### Configuration
- **root/.env** - Frontend config
- **backend/.env** - Backend config (✅ created)
- **backend/init_db.py** - Database initialization (✅ created)

---

## ✅ VERIFICATION CHECKLIST

Before declaring success:

- [ ] PostgreSQL running and database created
- [ ] Ollama running with mistral:latest
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] Can access http://localhost:5173 in browser
- [ ] Can view API docs at http://localhost:8000/docs
- [ ] Created a test crop plan successfully
- [ ] Crop appears in Crop Management page
- [ ] Irrigation schedule shows upcoming waterings
- [ ] Chatbot responds to messages
- [ ] Dashboard shows metrics without errors
- [ ] No console errors (F12 → Console)
- [ ] No backend/error logs (terminal shows clean run)

---

## 📞 SUPPORT & NEXT STEPS

### If Something Fails:
1. Check the Troubleshooting section above
2. Review the component's terminal for error messages
3. Check the browser console (F12)  
4. Restart the specific component (Ctrl+C, then re-run)

### To Extend the System:
1. Add more crops: `backend/crop_engine/crop_data.py`
2. Add new fields to forms: `src/pages/YieldInput.jsx`
3. Add new API endpoints: `backend/main.py`
4. Add new pages: Create `src/pages/NewPage.jsx` and add route

### To Deploy:
1. Build frontend: `npm run build` (creates `dist/` folder)
2. Deploy `dist/` to: Vercel, Netlify, or GitHub Pages
3. Deploy backend to: Heroku, Railway, or own server
4. Update `VITE_API_BASE_URL` in frontend to production backend URL

---

**Last Updated**: February 21, 2026  
**Status**: ✅ FULLY FUNCTIONAL & TESTED
