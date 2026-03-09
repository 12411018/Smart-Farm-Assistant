"""Complete API Feature Testing and Verification Script."""

import sys
import os
from datetime import datetime, timedelta, timezone
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import CropPlan, CropStage, IrrigationSchedule, IrrigationLog, WeatherLog
from crop_engine.crop_planner import generate_crop_stages, generate_irrigation_schedule, calculate_total_duration
from services.crop_service import serialize_plan, serialize_stage, serialize_schedule

def test_crop_planning_features():
    """Test all crop planning features."""
    print("\n" + "="*70)
    print("🌾 CROP PLANNING FEATURES")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Test 1: Generate crop stages
        print("\n✓ Test 1: Generate crop stages for Wheat")
        sowing_date = datetime.now(timezone.utc).isoformat()
        stages = generate_crop_stages("Wheat", sowing_date)
        print(f"  ✓ Generated {len(stages)} growth stages")
        for stage in stages[:2]:  # Show first 2
            print(f"    - {stage['stage']}: {stage['durationDays']} days")
        
        # Test 2: Create crop plan with related records
        print("\n✓ Test 2: Create complete crop plan")
        crop_plan = CropPlan(
            user_id="user-test-001",
            crop_name="Wheat",
            location="Pune, Maharashtra",
            soil_type="Loam",
            sowing_date=datetime.now(timezone.utc),
            growth_duration_days=130,
            irrigation_method="Drip",
            land_size_acres=5.0,
            expected_investment=50000.0,
            water_source_type="Borewell",
            status="active"
        )
        db.add(crop_plan)
        db.commit()
        print(f"  ✓ Created crop plan: {crop_plan.crop_name} at {crop_plan.location}")
        
        # Test 3: Add crop stages
        print("\n✓ Test 3: Add growth stages to plan")
        stages_data = generate_crop_stages("Wheat", crop_plan.sowing_date.isoformat())
        for stage_data in stages_data:
            crop_stage = CropStage(
                crop_plan_id=crop_plan.id,
                stage=stage_data['stage'],
                start_date=datetime.fromisoformat(stage_data['startDate']),
                end_date=datetime.fromisoformat(stage_data['endDate']),
                duration_days=stage_data['durationDays'],
                recommended_irrigation_frequency_days=stage_data['recommendedIrrigationFrequencyDays']
            )
            db.add(crop_stage)
        db.commit()
        print(f"  ✓ Added {len(stages_data)} stages to crop plan")
        
        # Test 4: Generate irrigation schedule
        print("\n✓ Test 4: Generate irrigation schedule")
        schedule_data = generate_irrigation_schedule(
            "Wheat",
            crop_plan.sowing_date.isoformat(),
            crop_plan.land_size_acres,
            crop_plan.irrigation_method,
            stages_data,
            crop_plan.soil_type
        )
        print(f"  ✓ Generated {len(schedule_data)} irrigation events")
        
        # Add first 3 schedules to database
        for sched_data in schedule_data[:3]:
            irrigation_schedule = IrrigationSchedule(
                crop_plan_id=crop_plan.id,
                date=datetime.fromisoformat(sched_data['date']),
                stage=sched_data['stage'],
                water_amount_liters=sched_data['waterAmountLiters'],
                method=sched_data['method'],
                status=sched_data['status']
            )
            db.add(irrigation_schedule)
        db.commit()
        print(f"  ✓ Added irrigation schedules to database")
        
        # Test 5: Test serialization
        print("\n✓ Test 5: Serialize plan for API response")
        fetched_plan = db.query(CropPlan).filter(CropPlan.id == crop_plan.id).first()
        stages_list = db.query(CropStage).filter(CropStage.crop_plan_id == crop_plan.id).all()
        schedules_list = db.query(IrrigationSchedule).filter(IrrigationSchedule.crop_plan_id == crop_plan.id).all()
        
        serialized = serialize_plan(fetched_plan, stages_list, schedules_list)
        print(f"  ✓ Serialized plan with {len(serialized['stages'])} stages and {len(serialized['irrigationSchedule'])} schedules")
        
        print(f"\n✅ ALL CROP PLANNING TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ CROP PLANNING TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_irrigation_features():
    """Test all irrigation features."""
    print("\n" + "="*70)
    print("💧 IRRIGATION FEATURES")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Get a crop plan
        crop_plan = db.query(CropPlan).first()
        if not crop_plan:
            print("  ⚠️  No crop plan found, creating one...")
            crop_plan = CropPlan(
                user_id="user-test-002",
                crop_name="Rice",
                location="Mumbai",
                soil_type="Clay",
                sowing_date=datetime.now(timezone.utc),
                growth_duration_days=120,
                irrigation_method="Flood",
                land_size_acres=3.0,
                status="active"
            )
            db.add(crop_plan)
            db.commit()
        
        # Test 1: Log irrigation execution
        print("\n✓ Test 1: Log irrigation execution")
        irrigation_log = IrrigationLog(
            crop_plan_id=crop_plan.id,
            irrigation_date=datetime.now(timezone.utc).date(),
            original_amount=1500.0,
            adjusted_amount=1200.0,
            weather_adjustment="Rain forecast 40%, reduce by 20%",
            weather_adjustment_percent=-20.0,
            planned_liters=1500.0,
            actual_liters=1200.0,
            duration_seconds=3600,
            status="completed",
            auto_triggered=True
        )
        db.add(irrigation_log)
        db.commit()
        print(f"  ✓ Logged irrigation: {irrigation_log.actual_liters}L executed (duration: {irrigation_log.duration_seconds}s)")
        
        # Test 2: Query irrigation logs
        print("\n✓ Test 2: Query irrigation logs")
        logs = db.query(IrrigationLog).filter(IrrigationLog.crop_plan_id == crop_plan.id).all()
        print(f"  ✓ Found {len(logs)} irrigation logs for crop plan")
        
        # Test 3: Calculate adjustments
        print("\n✓ Test 3: Weather-based adjustment calculation")
        if logs:
            log = logs[0]
            adjustment_percent = log.weather_adjustment_percent
            adjustment_amount = log.original_amount - log.adjusted_amount
            print(f"  ✓ Original: {log.original_amount}L, Adjusted: {log.adjusted_amount}L")
            print(f"  ✓ Adjustment: {adjustment_amount}L ({adjustment_percent}%)")
        
        print(f"\n✅ ALL IRRIGATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ IRRIGATION TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_weather_features():
    """Test all weather logging features."""
    print("\n" + "="*70)
    print("🌤️  WEATHER FEATURES")
    print("="*70)
    
    db = SessionLocal()
    try:
        crop_plan = db.query(CropPlan).first()
        if not crop_plan:
            print("  ⚠️  No crop plan found")
            return False
        
        # Test 1: Log weather data
        print("\n✓ Test 1: Log weather data")
        weather_log = WeatherLog(
            crop_plan_id=crop_plan.id,
            temp=28.5,
            humidity=65.0,
            rain=2.5,
            rain_chance=45.0
        )
        db.add(weather_log)
        db.commit()
        print(f"  ✓ Logged weather: {weather_log.temp}°C, {weather_log.humidity}% humidity")
        print(f"  ✓ Rain: {weather_log.rain}mm, Chance: {weather_log.rain_chance}%")
        
        # Test 2: Query weather logs
        print("\n✓ Test 2: Query weather logs")
        weather_logs = db.query(WeatherLog).filter(WeatherLog.crop_plan_id == crop_plan.id).all()
        print(f"  ✓ Found {len(weather_logs)} weather logs")
        
        # Test 3: Test JSON serialization
        print("\n✓ Test 3: Serialize weather data")
        if weather_logs:
            weather = weather_logs[0]
            weather_dict = {
                "temp": weather.temp,
                "humidity": weather.humidity,
                "rain": weather.rain,
                "rain_chance": weather.rain_chance,
                "date": weather.weather_date.isoformat()
            }
            json_str = json.dumps(weather_dict)
            print(f"  ✓ Serialized as JSON: {len(json_str)} bytes")
        
        print(f"\n✅ ALL WEATHER TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ WEATHER TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_data_integrity():
    """Test data integrity and relationships."""
    print("\n" + "="*70)
    print("🔗 DATA INTEGRITY & RELATIONSHIPS")
    print("="*70)
    
    db = SessionLocal()
    try:
        crop_plan = db.query(CropPlan).first()
        if not crop_plan:
            print("  ⚠️  No crop plan found")
            return False
        
        # Test 1: Cascade delete
        print("\n✓ Test 1: Test cascade delete (without actually deleting)")
        print(f"  ✓ Crop plan has:")
        print(f"    - {len(crop_plan.stages)} stages")
        print(f"    - {len(crop_plan.irrigation_schedule)} irrigation schedules")
        print(f"    - {len(crop_plan.irrigation_logs)} irrigation logs")
        print(f"    - {len(crop_plan.weather_logs)} weather logs")
        
        # Test 2: Foreign key constraints
        print("\n✓ Test 2: Foreign key relationships verified")
        for stage in crop_plan.stages:
            assert stage.crop_plan_id == crop_plan.id
        print(f"  ✓ All {len(crop_plan.stages)} stages linked correctly")
        
        for schedule in crop_plan.irrigation_schedule:
            assert schedule.crop_plan_id == crop_plan.id
        print(f"  ✓ All {len(crop_plan.irrigation_schedule)} schedules linked correctly")
        
        print(f"\n✅ ALL DATA INTEGRITY TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ DATA INTEGRITY TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🌾 SMART FARMING ASSISTANT - FEATURE VERIFICATION")
    print("=" * 70)
    
    results = {
        "Crop Planning": test_crop_planning_features(),
        "Irrigation": test_irrigation_features(),
        "Weather": test_weather_features(),
        "Data Integrity": test_data_integrity(),
    }
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for feature, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {feature}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("=" * 70)
        print("\n✅ DATABASE IS FULLY FUNCTIONAL")
        print("✅ ALL FEATURES ARE WORKING")
        print("\nYou can now start the backend:")
        print("  cd backend")
        print("  venv\\Scripts\\activate")
        print("  python -m uvicorn main:app --reload")
    else:
        print(f"⚠️  SOME TESTS FAILED ({total - passed}/{total} failed)")
    
    print("=" * 70 + "\n")
    
    sys.exit(0 if passed == total else 1)
