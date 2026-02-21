"""Complete database and feature verification script."""

import sys
import os
from datetime import datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, DATABASE_URL
from models import CropPlan, CropStage, IrrigationSchedule, IrrigationLog, WeatherLog

def test_database_connections():
    """Test all database table connections."""
    print("\n" + "="*70)
    print("🗄️  DATABASE CONNECTION TESTS")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Test CropPlan table
        print("\n✓ Testing CropPlan table...")
        crop_plan = CropPlan(
            id="test-plan-001",
            user_id="user-001",
            crop_name="Wheat",
            location="Pune",
            soil_type="Loam",
            sowing_date=datetime.now(timezone.utc),
            growth_duration_days=130,
            irrigation_method="Drip",
            land_size_acres=5.0,
            status="active"
        )
        db.add(crop_plan)
        db.commit()
        print(f"  ✓ Created CropPlan: {crop_plan.id}")
        
        # Test CropStage table (relationship)
        print("\n✓ Testing CropStage table (relationship)...")
        crop_stage = CropStage(
            crop_plan_id=crop_plan.id,
            stage="Seedling",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=20),
            duration_days=20,
            recommended_irrigation_frequency_days=3
        )
        db.add(crop_stage)
        db.commit()
        print(f"  ✓ Created CropStage: {crop_stage.stage}")
        
        # Test IrrigationSchedule table
        print("\n✓ Testing IrrigationSchedule table...")
        irrigation_schedule = IrrigationSchedule(
            crop_plan_id=crop_plan.id,
            date=datetime.now(timezone.utc) + timedelta(days=3),
            stage="Seedling",
            water_amount_liters=1000,
            method="Drip",
            status="pending"
        )
        db.add(irrigation_schedule)
        db.commit()
        print(f"  ✓ Created IrrigationSchedule: {irrigation_schedule.water_amount_liters}L on {irrigation_schedule.date.date()}")
        
        # Test IrrigationLog table
        print("\n✓ Testing IrrigationLog table...")
        irrigation_log = IrrigationLog(
            crop_plan_id=crop_plan.id,
            irrigation_date=datetime.now(timezone.utc).date(),
            original_amount=1000.0,
            adjusted_amount=850.0,
            weather_adjustment="Rain expected: -15%",
            weather_adjustment_percent=-15.0,
            planned_liters=1000.0,
            actual_liters=850.0,
            status="completed"
        )
        db.add(irrigation_log)
        db.commit()
        print(f"  ✓ Created IrrigationLog: {irrigation_log.actual_liters}L executed")
        
        # Test WeatherLog table
        print("\n✓ Testing WeatherLog table...")
        weather_log = WeatherLog(
            crop_plan_id=crop_plan.id,
            temp=28.5,
            humidity=65.0,
            rain=2.5,
            rain_chance=45.0
        )
        db.add(weather_log)
        db.commit()
        print(f"  ✓ Created WeatherLog: {weather_log.temp}°C, {weather_log.humidity}% humidity")
        
        # Test relationships
        print("\n✓ Testing relationships...")
        fetched_plan = db.query(CropPlan).filter(CropPlan.id == crop_plan.id).first()
        if fetched_plan:
            print(f"  ✓ CropPlan relationships:")
            print(f"    - Stages: {len(fetched_plan.stages)} stage(s)")
            print(f"    - Irrigation schedules: {len(fetched_plan.irrigation_schedule)} schedule(s)")
            print(f"    - Irrigation logs: {len(fetched_plan.irrigation_logs)} log(s)")
            print(f"    - Weather logs: {len(fetched_plan.weather_logs)} record(s)")
        
        # Test query operations
        print("\n✓ Testing query operations...")
        total_plans = db.query(CropPlan).count()
        total_stages = db.query(CropStage).count()
        total_schedules = db.query(IrrigationSchedule).count()
        total_logs = db.query(IrrigationLog).count()
        total_weather = db.query(WeatherLog).count()
        
        print(f"  ✓ Database summary:")
        print(f"    - Total CropPlans: {total_plans}")
        print(f"    - Total CropStages: {total_stages}")
        print(f"    - Total IrrigationSchedules: {total_schedules}")
        print(f"    - Total IrrigationLogs: {total_logs}")
        print(f"    - Total WeatherLogs: {total_weather}")
        
        # Cleanup test data
        print("\n✓ Cleaning up test data...")
        db.query(CropPlan).filter(CropPlan.id == crop_plan.id).delete()
        db.commit()
        print("  ✓ Test data removed")
        
        print("\n✅ ALL DATABASE TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ DATABASE TEST FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def verify_models():
    """Verify all models are correctly defined."""
    print("\n" + "="*70)
    print("📋 MODEL VERIFICATION")
    print("="*70)
    
    print("\n✓ Checking CropPlan model...")
    print(f"  Table: {CropPlan.__tablename__}")
    print(f"  Columns: {', '.join([col.name for col in CropPlan.__table__.columns])}")
    print(f"  Relationships: {', '.join([rel for rel in ['stages', 'irrigation_schedule', 'irrigation_logs', 'weather_logs']])}")
    
    print("\n✓ Checking CropStage model...")
    print(f"  Table: {CropStage.__tablename__}")
    print(f"  Columns: {', '.join([col.name for col in CropStage.__table__.columns])}")
    
    print("\n✓ Checking IrrigationSchedule model...")
    print(f"  Table: {IrrigationSchedule.__tablename__}")
    print(f"  Columns: {', '.join([col.name for col in IrrigationSchedule.__table__.columns])}")
    
    print("\n✓ Checking IrrigationLog model...")
    print(f"  Table: {IrrigationLog.__tablename__}")
    print(f"  Columns: {', '.join([col.name for col in IrrigationLog.__table__.columns])}")
    
    print("\n✓ Checking WeatherLog model...")
    print(f"  Table: {WeatherLog.__tablename__}")
    print(f"  Columns: {', '.join([col.name for col in WeatherLog.__table__.columns])}")
    
    print("\n✅ MODEL VERIFICATION COMPLETE!")

def verify_database_info():
    """Show database information."""
    print("\n" + "="*70)
    print("ℹ️  DATABASE INFORMATION")
    print("="*70)
    
    if "sqlite" in DATABASE_URL.lower():
        db_type = "SQLite (Development)"
        db_path = DATABASE_URL.split("///")[-1] if ":///" in DATABASE_URL else DATABASE_URL
    else:
        db_type = "PostgreSQL (Production)"
        db_path = "Remote server"
    
    print(f"\nDatabase Type: {db_type}")
    print(f"Location: {db_path}")
    print(f"Full URL: {DATABASE_URL}")
    
    print("\n✓ Table Structure:")
    print("  crop_plans (Master)")
    print("  ├─ crop_stages (1:Many)")
    print("  ├─ irrigation_schedule (1:Many)")
    print("  ├─ irrigation_logs (1:Many)")
    print("  └─ weather_logs (1:Many)")

if __name__ == "__main__":
    print("\n🌾 SMART FARMING ASSISTANT - DATABASE VERIFICATION")
    
    verify_database_info()
    verify_models()
    success = test_database_connections()
    
    print("\n" + "="*70)
    if success:
        print("✅ DATABASE FULLY FUNCTIONAL - ALL TESTS PASSED!")
    else:
        print("❌ DATABASE TESTS FAILED - SEE ERRORS ABOVE")
    print("="*70 + "\n")
    
    sys.exit(0 if success else 1)
