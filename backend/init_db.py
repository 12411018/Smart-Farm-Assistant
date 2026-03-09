"""Database initialization script - Creates all tables and sets up the database."""

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables BEFORE importing database module
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

from database import Base, DATABASE_URL
from models import CropPlan, CropStage, IrrigationSchedule, IrrigationLog, WeatherLog, User

def setup_database():
    """Initialize database with all tables."""
    print("🔧 Smart Farming Assistant - Database Setup")
    print("=" * 60)
    
    # Check if using SQLite or PostgreSQL
    if "sqlite" in DATABASE_URL.lower():
        print(f"📦 Database: SQLite (Development)")
        print(f"   Location: {DATABASE_URL.split(':///')[-1]}")
    else:
        print(f"📦 Database: PostgreSQL (Production)")
        # Hide password in URL display
        display_url = DATABASE_URL.replace(DATABASE_URL.split(':')[2].split('@')[0], '***')
        print(f"   URL: {display_url}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL, future=True, echo=False)
        
        # Test connection
        print("\n✓ Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                print("✓ Database connection successful!")
        
        # Create all tables
        print("\n✓ Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created/verified!")
        
        # Verify tables exist
        print("\n✓ Verifying table structure...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        table_names = [
            "users",
            "crop_plans",
            "crop_stages", 
            "irrigation_schedule",
            "irrigation_logs",
            "weather_logs"
        ]
        
        print(f"   Expected tables: {len(table_names)}")
        missing_tables = []
        for table in table_names:
            if table in existing_tables:
                print(f"   ✓ {table}")
            else:
                print(f"   ✗ {table} (MISSING)")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ WARNING: {len(missing_tables)} tables missing!")
            raise Exception(f"Tables not created: {missing_tables}")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Create backend/.env file with SECRET_KEY")
        print("   2. Run: npm run dev (frontend)")
        print("   3. Run: python -m uvicorn main:app --reload (backend)")
        print("\n💡 Database tables created:")
        print("   • users - User authentication")
        print("   • crop_plans - Master crop records")
        print("   • crop_stages - Growth stages timeline")
        print("   • irrigation_schedule - Planned irrigations")
        print("   • irrigation_logs - Executed irrigations")
        print("   • weather_logs - Historical weather data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DATABASE SETUP FAILED!")
        print(f"Error: {str(e)}")
        print("\n⚠️ Troubleshooting:")
        
        if "postgresql" in DATABASE_URL.lower():
            print("   For PostgreSQL:")
            print("   1. Ensure PostgreSQL is running")
            print("   2. Check database credentials:")
            print("      - User: meet")
            print("      - Password: meet")
            print("      - Host: localhost")
            print("      - Port: 5432")
            print("      - Database: smart_irrigation")
            print("   3. Or set custom DATABASE_URL in backend/.env")
            print("   4. Or use SQLite instead: DATABASE_URL=sqlite:///./smart_farming.db")
        
        print("\n   For SQLite (Fallback):")
        print("   1. Set in backend/.env: DATABASE_URL=sqlite:///./smart_farming.db")
        print("   2. Re-run this script")
        
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
