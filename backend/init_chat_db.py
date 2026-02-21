"""Initialize database tables for chat history"""

from database import engine, Base
from models import Conversation, Message

def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("   - conversations")
    print("   - messages")

if __name__ == "__main__":
    init_db()
