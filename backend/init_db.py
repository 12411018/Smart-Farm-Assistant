#!/usr/bin/env python3
"""
Database initialization script for Smart Farming Assistant.
Creates tables, initializes schema, and verifies connectivity.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from dotenv import load_dotenv

# Load environment
env_path = Path(backend_path) / '.env'
load_dotenv(dotenv_path=env_path)

from database import engine, Base
from models import CropPlan, CropStage, IrrigationSchedule, IrrigationLog, WeatherLog

def init_db():
    """Initialize database and create all tables."""
    print("=" * 70)
    print("🌾 SMART FARMING ASSISTANT - DATABASE INITIALIZATION")
    print("=" * 70)
    print()
    
    # Check database connection
    try:
        print("1️⃣  Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("   ✅ Database connection successful!")
        print()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and credentials are correct.")
        return False
    
    # Create all tables
    try:
        print("2️⃣  Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tables created successfully!")
        print("      - CropPlan")
        print("      - CropStage")
        print("      - IrrigationSchedule")
        print("      - IrrigationLog")
        print("      - WeatherLog")
        print()
    except Exception as e:
        print(f"   ❌ Failed to create tables: {e}")
        return False
    
    # Verify tables exist
    try:
        print("3️⃣  Verifying tables...")
        inspector_query = """
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public'
        """
        with engine.connect() as conn:
            result = conn.execute(inspector_query)
            tables = [row[0] for row in result]
            expected_tables = [
                'crop_plans',
                'crop_stages', 
                'irrigation_schedule',
                'irrigation_logs',
                'weather_logs'
            ]
            for table in expected_tables:
                if table in tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (MISSING)")
        print()
    except Exception as e:
        print(f"   ⚠️  Could not verify tables: {e}")
        print("      (Tables may still work, continuing...)")
        print()
    
    # Summary
    print("=" * 70)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start the backend server:")
    print("     uvicorn main:app --reload")
    print("  2. Run the frontend:")
    print("     npm run dev")
    print("  3. Create a crop plan from the UI")
    print()
    return True

if __name__ == '__main__':
    try:
        success = init_db()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
