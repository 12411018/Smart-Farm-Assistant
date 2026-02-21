"""Database configuration for PostgreSQL persistence."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to provided local connection string; allow override via env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Default fallback uses the project DB name and the password provided by the user.
    # Note: '@' in passwords must be URL-encoded as '%40'.
    "postgresql+psycopg2://postgres:purva%402006@localhost:5432/smart_irrigation",
)

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """Yield a SQLAlchemy session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
