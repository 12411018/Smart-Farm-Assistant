from database import SessionLocal
from models import Conversation

db = SessionLocal()
conv = db.query(Conversation).filter_by(user_id='default_user').order_by(Conversation.created_at.desc()).first()

if conv:
    print(f'Latest conversation:')
    print(f'  Title: {conv.title}')
    print(f'  Messages: {len(conv.messages)}')
    print(f'  Created: {conv.created_at}')
    if conv.messages:
        print(f'  First message: {conv.messages[0].content}')
else:
    print('No conversations found')

db.close()
