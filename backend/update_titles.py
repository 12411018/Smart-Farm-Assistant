"""Update old 'New Conversation' titles with smart titles based on first message."""
from database import SessionLocal
from models import Conversation, Message
import re

def generate_conversation_title(message: str) -> str:
    """Generate a concise, meaningful title from the first message."""
    clean_msg = " ".join(message.strip().split())
    sentences = re.split(r'[.!?]+', clean_msg)
    first_sentence = sentences[0].strip() if sentences else clean_msg
    
    title = first_sentence
    question_patterns = [
        (r'^(how|what|when|where|why|which|who)\s+(do|does|did|can|could|should|would|will|shall)\s+(i|you|we|they)\s+', ''),
        (r'^(how)\s+(to)\s+', ''),
        (r'^(how|what|when|where|why|which|who)\s+(is|are|was|were|do|does|did|can|could|should|would|will|shall)\s+', ''),
        (r'^(how|what|when|where|why|which|who)\s+', ''),
        (r'^(is|are|was|were|do|does|did|can|could|should|would|will|shall)\s+', ''),
        (r'^(tell me|show me|explain|give me)\s+(about\s+)?', ''),
    ]
    
    for pattern, replacement in question_patterns:
        new_title = re.sub(pattern, replacement, title, flags=re.IGNORECASE)
        if new_title != title and len(new_title.strip()) > 0:
            title = new_title.strip()
            break
    
    title = title.strip()
    if title:
        title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
    
    max_length = 50
    if len(title) > max_length:
        title = title[:max_length].rsplit(' ', 1)[0]
        if len(title) < 20:
            title = first_sentence[:max_length]
        title = title.rstrip('.,!?;:') + '...'
    
    return title if title else "New conversation"

db = SessionLocal()

# Find conversations with "New Conversation" title that have messages
convs = db.query(Conversation).filter(
    Conversation.title.in_(["New Conversation", "New conversation"])
).all()

print(f"Found {len(convs)} conversations with 'New Conversation' title")
print("=" * 70)

updated_count = 0
for conv in convs:
    # Get first user message
    first_msg = db.query(Message).filter(
        Message.conversation_id == conv.id,
        Message.role == 'user'
    ).order_by(Message.timestamp).first()
    
    if first_msg:
        new_title = generate_conversation_title(first_msg.content)
        print(f"Updating: {conv.id}")
        print(f"  From: {conv.title}")
        print(f"  To:   {new_title}")
        print(f"  First message: {first_msg.content[:60]}")
        print()
        
        conv.title = new_title
        updated_count += 1

db.commit()
db.close()

print("=" * 70)
print(f"✅ Updated {updated_count} conversation titles")
