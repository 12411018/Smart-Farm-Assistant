"""
Database configuration supporting PostgreSQL and SQLite.
"""

import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meet:meet@localhost:5432/smart_irrigation"
)

print(
    f"📊 Using Database: "
    f"{DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'SQLite'}"
)

# -------------------------
# Engine Creation
# -------------------------
if "postgresql" in DATABASE_URL.lower():

    engine = create_engine(
        DATABASE_URL,
        future=True,
        echo=False,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
    )

    print("✅ PostgreSQL engine created")

else:
    engine = create_engine(
        DATABASE_URL,
        future=True,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    print("✅ SQLite engine created")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

Base = declarative_base()


# -------------------------
# Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# IMPORT MODELS + CREATE TABLES
# -------------------------
import models   # ⭐ REQUIRED

Base.metadata.create_all(bind=engine)

print("✅ Tables created / verified")