# Sensor Integration Testing Guide

## Setup
1. Backend running on `http://localhost:8000`
2. Create a crop plan via Calendar page (get the `crop_plan_id`)
3. Copy the `crop_plan_id` from the URL or response

## Test Endpoints

### 1. Raindrop Sensor - Skip Irrigation
When rain >= 5mm is detected, irrigation is automatically SKIPPED.

```bash
# Get crop_plan_id from your plan
PLAN_ID="your-crop-plan-id-here"

# Simulate rain detection (6.5mm)
curl -X POST "http://localhost:8000/sensor/raindrop?crop_plan_id=$PLAN_ID&rain_mm=6.5"

# Expected Response:
# {
#   "action": "SKIP",
#   "reason": "Rain 6.5mm detected",
#   "status": "skipped"
# }

# Check /irrigation/schedule - today's water should be 0L and status "skipped"
```

---

### 2. DHT11 Sensor - Adjust Water Based on Temperature & Humidity

Adjustments applied:
- **Temperature > 35°C**: +15% water (more evaporation)
- **Humidity < 30%**: +10% water (dry air)
- **Humidity > 85% + Temp < 28°C**: -15% water (low evaporation)

```bash
# Example 1: Hot & Dry conditions (should increase water)
curl -X POST "http://localhost:8000/sensor/dht11?crop_plan_id=$PLAN_ID&temperature=36.5&humidity=25"

# Expected: Water increased by ~25% (15% + 10%)
# {
#   "status": "adjusted",
#   "original_liters": 100,
#   "adjusted_liters": 126,
#   "adjustment_percent": 26.0,
#   "reasons": [
#     "High temp 36.5°C: +15%",
#     "Low humidity 25%: +10%"
#   ]
# }

# Example 2: Cool & Humid (should decrease water)
curl -X POST "http://localhost:8000/sensor/dht11?crop_plan_id=$PLAN_ID&temperature=25.0&humidity=88"

# Expected: Water decreased by ~15%
```

---

### 3. Soil Moisture Sensor - Skip or Increase Water

Logic:
- **Moisture >= 80%**: SKIP irrigation (soil too wet)
- **Moisture < 35%**: +20% water (soil too dry)
- **35-80%**: No change (optimal)

```bash
# Example 1: Soil too wet - skip irrigation
curl -X POST "http://localhost:8000/sensor/soil-moisture?crop_plan_id=$PLAN_ID&moisture_percent=82"

# Expected: Irrigation SKIPPED
# {
#   "action": "SKIP",
#   "reason": "Soil too wet (82%)",
#   "status": "skipped"
# }

# Example 2: Soil too dry - increase water
curl -X POST "http://localhost:8000/sensor/soil-moisture?crop_plan_id=$PLAN_ID&moisture_percent=30"

# Expected: Water increased by 20%
# {
#   "status": "increased",
#   "reason": "Soil dry (30%)",
#   "original_liters": 100,
#   "adjusted_liters": 120,
#   "adjustment_percent": 20
# }

# Example 3: Optimal moisture - no change
curl -X POST "http://localhost:8000/sensor/soil-moisture?crop_plan_id=$PLAN_ID&moisture_percent=55"

# Expected: No change
# {
#   "status": "optimal",
#   "moisture_percent": 55,
#   "action": "OK"
# }
```

---

## Demo Sequence (For Hackathon Judges)

1. **Create Crop Plan** → Get initial schedule (e.g., 100L needed today)

2. **Simulate Hot & Dry** 
   ```bash
   curl -X POST "http://localhost:8000/sensor/dht11?crop_plan_id=$PLAN_ID&temperature=38&humidity=22"
   ```
   → Schedule updates: **100L → 126L** (show water increase) ✅

3. **Simulate Rain Event**
   ```bash
   curl -X POST "http://localhost:8000/sensor/raindrop?crop_plan_id=$PLAN_ID&rain_mm=7"
   ```
   → Schedule updates: **126L → 0L, Status SKIPPED** ✅

4. **Check Calendar** 
   → See today's event shows "Skipped - Rain detected" ✅

5. **Check Irrigation Logs**
   → See all adjustments logged with sensor data ✅

---

## Backend Console Output

You'll see logs like:
```
[SENSOR] DHT11: temp=38°C, humidity=22% → Adjusted 100L → 126L (+26.0%)
[SENSOR] Raindrop: 7mm detected → Irrigation SKIPPED for plan xxx
[SENSOR] Soil Moisture: 30% (dry) → Adjusted 100L → 120L
```

---

## Integration with Firebase (Real-time Demo)

Sensor values update every minute from Firebase:
- **Raindrop Sensor**: Triggers `/sensor/raindrop` when rain detected
- **DHT11**: Triggers `/sensor/dht11` every minute with latest temp/humidity
- **Soil Moisture**: Triggers `/sensor/soil-moisture` every minute with latest reading

**Your Arduino/IoT device should call these endpoints when sensor values change.**

---

## Verify Everything is Working

After each sensor call:

1. **Check schedule updated**:
   ```bash
   curl "http://localhost:8000/irrigation/schedule/$PLAN_ID"
   ```
   → Water liters should reflect sensor adjustments

2. **Check logs created**:
   ```bash
   # In Calendar page, click on today
   # You should see irrigation event with adjustment notes
   ```

3. **Check next command**:
   ```bash
   curl "http://localhost:8000/irrigation/next-command/$PLAN_ID?lat=18.45&lon=73.87"
   ```
   → Should return `action: SKIP` or `action: WATER` with adjusted amount

---

## No Disruption ✅

- Existing endpoints (`/irrigation/schedule`, `/calendar`, `/next-command`) work unchanged
- Sensor data only updates today's schedule entry
- All historical logs preserved
- Can call sensors in any order
- Safe to test without affecting other features
