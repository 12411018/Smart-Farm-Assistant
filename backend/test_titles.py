"""Test script to demonstrate smart title generation."""
from database import SessionLocal
from models import Conversation

db = SessionLocal()

# Get recent conversations with demo users
convs = db.query(Conversation).filter(
    Conversation.user_id.like('demo_%')
).order_by(Conversation.created_at.desc()).limit(10).all()

print("=" * 70)
print("SMART TITLE GENERATION EXAMPLES")
print("=" * 70)
print()

if convs:
    for conv in convs:
        print(f"Title: {conv.title}")
        # Get first message to show original query
        if conv.messages:
            first_msg = conv.messages[0]
            print(f"Original: {first_msg.content}")
        print()
else:
    print("No demo conversations found yet.")
    print("Send a message through the chatbot to see title generation in action!")

db.close()
