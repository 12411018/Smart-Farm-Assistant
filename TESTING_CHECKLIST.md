# 🚀 Complete System Testing Checklist

## ✅ Pre-Flight Checks

### 1. Backend Dependencies
- [ ] Ollama installed and running (`ollama list` shows `mistral:latest`)
- [ ] Python packages installed (`firebase-admin` added)
- [ ] `.env` configured with `OPENWEATHER_API_KEY`
- [ ] Firebase project ID set (optional: `FIREBASE_PROJECT_ID=smart-irrigation-system-f87ad`)

### 2. Frontend Dependencies
- [ ] `react-calendar` installed
- [ ] `react-markdown` installed

### 3. Servers Running
- [ ] Backend: `http://127.0.0.1:8000` (check `/health` endpoint)
- [ ] Frontend: `http://localhost:5173`
- [ ] Ollama: `http://localhost:11434` (check `GET /api/tags`)

---

## 🧪 Feature Testing

### Phase 1: Weather System
1. [ ] Navigate to **Weather** page
2. [ ] Allow browser location permission
3. [ ] Verify location shows city/state/country (e.g., "Pune, Maharashtra, IN")
4. [ ] Check current weather displays
5. [ ] Verify 24-hour forecast scrolls horizontally
6. [ ] Verify 7-day forecast scrolls horizontally
7. [ ] Check **Irrigation Decision** badge shows (NORMAL/SKIP/INCREASE/REDUCE)
8. [ ] Verify **AI Weather Insights** loads (may take 10-20s first time)
9. [ ] Check pest/disease/spray/fertilizer warnings display

### Phase 2: Chatbot (RAG)
1. [ ] Navigate to **Chatbot** page
2. [ ] Ask: "What crops grow well in black soil?"
3. [ ] Verify "Thinking..." bubble appears
4. [ ] Check response has markdown formatting
5. [ ] Verify response is relevant (uses RAG context)
6. [ ] Ask follow-up: "What about cotton irrigation?"
7. [ ] Check chat history is maintained
8. [ ] Verify auto-scroll to latest message

### Phase 3: Yield Input (Crop Planning)
1. [ ] Navigate to **Yield Input** page
2. [ ] Fill form:
   - Crop: **Wheat**
   - Sowing Date: **Today's date**
   - Location: **Pune, Maharashtra**
   - Soil Type: **Black**
   - Irrigation Method: **Drip**
   - Land Size: **5 acres**
   - Expected Investment: **50000** (optional)
   - Water Source: **Borewell**
3. [ ] Click "Generate Crop Plan"
4. [ ] Verify success message with Plan ID shows
5. [ ] Check Firebase Console → Firestore has:
   - [ ] `crop_plans` collection with 1 document
   - [ ] `crop_calendar` collection with 5 documents (Wheat has 5 stages)
   - [ ] `irrigation_schedule` collection with ~15-20 documents

### Phase 4: Crop Calendar
1. [ ] Navigate to **Calendar** page
2. [ ] Verify crop plan dropdown shows created plan
3. [ ] Check calendar displays with color-coded tiles
4. [ ] Verify **Current Stage** shows "Germination"
5. [ ] Click on a future date
6. [ ] Verify selected date info displays growth stage
7. [ ] Check irrigation markers (💧) appear on schedule days
8. [ ] Verify **Growth Timeline** shows all 5 stages
9. [ ] Check **AI Crop Insights** loads (10-20s)
10. [ ] Verify **Upcoming Irrigation** list shows next 3 events

### Phase 5: Weather Adjustment (Advanced)
1. [ ] In browser console or API client, call:
   ```
   POST http://127.0.0.1:8000/irrigation/adjust?crop_plan_id=YOUR_PLAN_ID&lat=18.45&lon=73.87
   ```
2. [ ] Check response shows adjustments made
3. [ ] Verify Firebase `irrigation_logs` collection has new entries
4. [ ] Reload Calendar page
5. [ ] Check if irrigation amounts changed based on weather

---

## 🎯 Demo Flow (For Judges/Presentation)

### Scenario: "Farmer Raj wants to plant wheat"

**Step 1: Create Crop Plan** (2 mins)
1. Open **Yield Input**
2. Select Wheat, fill details, submit
3. Show success message with Plan ID
4. Open Firebase Console → show 3 collections created

**Step 2: View Calendar** (2 mins)
1. Open **Calendar**
2. Show color-coded growth stages
3. Click on dates to show irrigation schedule
4. Highlight AI insights panel

**Step 3: Weather Integration** (2 mins)
1. Open **Weather**
2. Show live location detection
3. Point out irrigation decision badge
4. Explain how it affects the schedule

**Step 4: AI Q&A** (1 min)
1. Open **Chatbot**
2. Ask crop-specific question
3. Show RAG-powered response

**Step 5: Data Logging** (1 min)
1. Back to Firebase Console
2. Show `irrigation_logs` with weather adjustments
3. Explain production-ready architecture

**Total Demo Time**: ~8 minutes

---

## 🐛 Common Issues & Fixes

### Issue: "Unable to load weather data"
**Fix**: 
- Check `OPENWEATHER_API_KEY` in `backend/.env`
- Restart backend server
- Allow browser location permission

### Issue: "No Crop Plans Yet" in Calendar
**Fix**: 
- Create a plan from Yield Input first
- Check backend console for errors
- Verify Firebase connection

### Issue: AI insights not loading
**Fix**:
- Check Ollama is running: `ollama run mistral:latest`
- First query takes 10-20s (model loading)
- Check backend logs for Mistral errors

### Issue: Calendar tiles not colored
**Fix**:
- Check crop plan has stages (backend response)
- Verify dates are within stage ranges
- Hard refresh browser (Ctrl+Shift+R)

### Issue: Firebase errors
**Fix**:
- System works WITHOUT Firebase (features disabled gracefully)
- Set `FIREBASE_PROJECT_ID` in `.env`
- Or generate service account key (see FIREBASE_SETUP.md)

---

## 📊 Expected Results

### Backend Health Check
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"ok"}
```

### Test Crop Plan Creation
```bash
curl -X POST http://127.0.0.1:8000/crop-plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user",
    "cropName": "Wheat",
    "location": "Pune",
    "soilType": "Black",
    "sowingDate": "2026-02-12",
    "irrigationMethod": "Drip",
    "landSizeAcres": 5,
    "waterSourceType": "Borewell"
  }'
```

Should return:
```json
{
  "success": true,
  "cropPlanId": "abc123...",
  "stages": [...5 stages...],
  "irrigationSchedule": [...15-20 items...],
  "totalDurationDays": 120
}
```

---

## ✨ Hackathon Judging Points

### Technical Excellence
- ✅ Clean architecture (separation of concerns)
- ✅ Production-ready code (error handling, logging)
- ✅ Scalable database design (Firebase Firestore)
- ✅ Local AI (cost-effective)

### Innovation
- ✅ Weather-integrated irrigation automation
- ✅ AI-powered crop insights (separate from chatbot)
- ✅ Real-time location-based decisions
- ✅ Automated adjustment logging

### Practical Impact
- ✅ Solves real farmer problem (water optimization)
- ✅ Data-driven decisions
- ✅ Long-term crop planning
- ✅ Reduces manual planning effort

### Presentation
- ✅ Visual calendar interface
- ✅ Live data demonstration
- ✅ Firebase backend showcase
- ✅ Complete end-to-end flow

---

## 🎓 Knowledge Transfer

### For Teammates
1. **Backend Routes**: See `backend/main.py` lines 180-380
2. **Crop Planning Logic**: See `backend/crop_engine/crop_planner.py`
3. **Calendar Component**: See `src/pages/CropCalendar.jsx`
4. **Firebase Schema**: See README.md "Firestore Collections"

### For Judges
- Architecture diagram: See README.md
- API documentation: See README.md "API Documentation"
- Live Firebase data: Show Firestore Console during demo

---

## 🏁 Final Checks Before Demo

- [ ] All servers running
- [ ] At least 1 crop plan created
- [ ] Firebase Console open in browser tab
- [ ] Weather page shows live location
- [ ] Calendar shows colored stages
- [ ] Chatbot responds to questions
- [ ] Backend logs clean (no errors)

**Ready to win! 🏆**
