# Chat History Setup Guide

## Overview
This guide helps you set up the PostgreSQL-based chat history feature for the Smart Farm Assistant chatbot.

## Prerequisites
- PostgreSQL server running
- Database: `smart_irrigation` created
- Backend dependencies installed (already done)

## Setup Steps

### 1. Initialize Database Tables

Run the initialization script to create the chat history tables:

```bash
cd backend
python init_chat_db.py
```

This will create two tables:
- `conversations` - Stores chat conversations
- `messages` - Stores individual messages

### 2. Restart Backend

If your backend is running, restart it to load the new models:

```bash
# Stop current backend (Ctrl+C)
python run.py
```

### 3. Start Frontend

Make sure your frontend is running:

```bash
cd ..  # Back to Smart-Farm-Assistant root
npm run dev
```

### 4. Test the Feature

1. Open http://localhost:5173/chatbot
2. You should see a chat history sidebar on the left
3. Send a message - it will create a new conversation
4. The conversation will appear in the sidebar
5. Click on conversations to switch between them
6. Hover over conversations to see the delete button

## Features

### Chat History Sidebar
- **New Chat Button** - Create a new conversation
- **Conversation List** - Shows all your conversations
- **Active Highlighting** - Current conversation is highlighted
- **Delete** - Remove conversations (hover to see button)
- **Auto-title** - First message becomes conversation title

### Database Persistence
- All messages are saved to PostgreSQL
- Conversations persist across browser refreshes
- Messages are loaded when you select a conversation

### API Endpoints (Already Implemented)
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations?user_id=<id>` - List all conversations
- `GET /api/conversations/{id}` - Get conversation with messages
- `DELETE /api/conversations/{id}` - Delete conversation
- `PATCH /api/conversations/{id}` - Update conversation
- `POST /chat` - Send message (updated to save to DB)

## Troubleshooting

### Database Connection Error
If you see database errors:
1. Check PostgreSQL is running
2. Verify connection string in `backend/database.py`
3. Ensure database `smart_irrigation` exists

### Tables Not Created
If init_chat_db.py doesn't work:
```bash
# Connect to PostgreSQL
psql -U postgres -d smart_irrigation

# Manually create tables
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE INDEX ix_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER DEFAULT 0
);

CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
```

### Sidebar Not Showing
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check that ChatHistory component is imported in Chatbot.jsx

### Messages Not Saving
1. Check backend console for errors
2. Verify database connection
3. Check that `conversation_id` is being sent in requests

## UI Customization

### Change Sidebar Width
Edit `src/styles/ChatHistory.css`:
```css
.chat-history {
  width: 280px;  /* Change this value */
  min-width: 280px;
}
```

### Change Color Theme
The sidebar uses the same color palette as the main chatbot:
- Primary green: `var(--primary-green)`
- Light green: `var(--light-green)`

## User ID Management

Currently using `default_user` as the user ID. To add real user authentication:

1. **Firebase Auth** (already integrated):
   ```jsx
   import { getAuth } from 'firebase/auth';
   const auth = getAuth();
   const userId = auth.currentUser?.uid || 'default_user';
   ```

2. **localStorage**:
   ```jsx
   const userId = localStorage.getItem('userId') || 'default_user';
   ```

3. **URL parameter**:
   ```jsx
   const userId = new URLSearchParams(window.location.search).get('user') || 'default_user';
   ```

## Next Steps

Consider adding:
- Search across conversations
- Export conversation as text/PDF
- Archive conversations instead of deleting
- Conversation tags/categories
- Pin important conversations
- Edit conversation titles

## Support

If you encounter issues:
1. Check console logs (both frontend and backend)
2. Verify database connection
3. Ensure all dependencies are installed
4. Restart both backend and frontend servers
