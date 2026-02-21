# Chat History Feature - Implementation Guide

## Overview

This document describes the Chat History feature implemented in your local codebase. This feature is **NOT present** in the GitHub repository (https://github.com/12411018/Smart-Farm-Assistant.git) and represents a significant enhancement.

---

## What is Chat History?

A complete conversation management system that allows users to:
- Save all chat conversations to PostgreSQL database
- View conversation history in a sidebar
- Create new conversations
- Delete old conversations
- Retrieve conversations across browser sessions
- Auto-generate smart conversation titles

---

## Components

### 1. Frontend Components

#### ChatHistory.jsx
**Location:** `src/components/ChatHistory.jsx`

**Features:**
- Sidebar displaying all user conversations
- "New Conversation" button
- Conversation list with titles, message counts, and timestamps
- Delete button for each conversation
- Refresh mechanism triggered by parent component

**Key Functions:**
- `loadConversations()` - Fetches user's conversations from backend
- `handleNewConversation()` - Creates new empty conversation
- `handleSelectConversation()` - Switches to selected conversation
- `handleDeleteConversation()` - Removes conversation from database

**API Calls:**
```javascript
GET /api/conversations?user_id={userId}
POST /api/conversations
DELETE /api/conversations/{id}
```

#### Chatbot.jsx (Enhanced)
**Location:** `src/pages/Chatbot.jsx`

**Enhancements:**
- Integrated ChatHistory sidebar
- `getUserId()` function for persistent user identification via localStorage
- `currentConversationId` state for tracking active conversation
- `refreshHistory` trigger for updating sidebar after messages
- Smooth loading transitions when switching conversations

**localStorage Key:** `smart_farm_user_id`
**Format:** `user_${timestamp}_${random}`

---

### 2. Backend Components

#### Database Models
**Location:** `backend/models.py` (lines 130-155)

**Conversation Model:**
```python
class Conversation(Base):
    __tablename__ = "conversations"
    
    id: UUID (primary key)
    user_id: String (indexed)
    title: String (default: "New Conversation")
    created_at: DateTime
    updated_at: DateTime  
    is_archived: Boolean
    
    messages: relationship (one-to-many)
```

**Message Model:**
```python
class Message(Base):
    __tablename__ = "messages"
    
    id: UUID (primary key)
    conversation_id: UUID (foreign key → conversations.id)
    role: String ('user' or 'assistant')
    content: Text
    timestamp: DateTime
    tokens_used: Integer (optional)
    
    conversation: relationship (many-to-one)
```

#### API Endpoints
**Location:** `backend/main.py` (lines ~900-1100)

**GET /api/conversations**
- Returns all conversations for a user
- Query parameter: `user_id`
- Response: List of ConversationResponse objects

**POST /api/conversations**
- Creates new conversation
- Request body: `{user_id: string, title: string}`
- Response: ConversationResponse with new ID

**GET /api/conversations/{conversation_id}/messages**
- Returns all messages in a conversation
- Response: List of MessageResponse objects

**DELETE /api/conversations/{conversation_id}**
- Deletes conversation and all messages (cascade)
- Response: Success confirmation

**Enhanced /chat Endpoint:**
- Now saves messages to database
- Auto-generates smart titles from first message
- Updates "New Conversation" placeholder titles
- Uses regex to extract meaningful keywords

#### Smart Title Generation
**Location:** `backend/main.py` (lines ~350-380)

```python
def generate_conversation_title(message: str, max_length: int = 50) -> str:
    """
    Remove question words, extract keywords, capitalize
    Example: "How to grow tomatoes?" → "Grow tomatoes"
    """
```

**Features:**
- Removes common question words (how, what, why, etc.)
- Strips special characters
- Capitalizes first letter
- Truncates to max_length
- Falls back to "New Conversation" if parsing fails

---

### 3. Database Schema

**Tables Created:**

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_archived BOOLEAN DEFAULT FALSE,
    INDEX idx_user_id (user_id)
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    INDEX idx_conversation_id (conversation_id)
);
```

**Migration Script:**
`backend/init_chat_db.py` - Creates tables if they don't exist

---

### 4. Styling

**ChatHistory.css**
**Location:** `src/styles/ChatHistory.css`

**Features:**
- Fixed sidebar with scroll
- Hover effects on conversation items
- Delete button with confirmation styling
- Active conversation highlighting
- Responsive design (hides on mobile)

**Enhanced Chatbot.css**
- Better padding for messages (1.4rem 1.6rem)
- Smooth fade transitions
- Markdown-friendly styling
- Loading state indicators

---

## User Flow

### First-Time User:
1. User visits chatbot
2. `getUserId()` creates unique ID in localStorage
3. No conversations exist yet
4. Default welcome message appears
5. User sends first message
6. New conversation auto-created in database
7. Title auto-generated from first message
8. Conversation appears in sidebar

### Returning User:
1. User visits chatbot
2. `getUserId()` retrieves existing ID from localStorage
3. Sidebar loads all user's conversations from database
4. User can:
   - Click conversation to load it
   - Create new conversation
   - Delete old conversations
   - Continue chatting (messages auto-saved)

---

## Data Persistence

### Session Persistence:
- User ID stored in `localStorage.smart_farm_user_id`
- Survives browser close/reopen
- Deleted only if user clears browser data

### Database Persistence:
- All conversations saved to PostgreSQL
- Messages linked to conversations via foreign key
- Cascade delete: deleting conversation removes all messages
- Timestamps for sorting and display

---

## Current Statistics

**Your Database (as of last check):**
- 30 conversations stored
- 56 messages across conversations
- 6+ unique users (based on user_id)
- All entries have proper timestamps
- Smart titles generated for all non-placeholder conversations

---

## API Integration

### Frontend → Backend Flow:

1. **Load Conversations:**
   ```javascript
   fetch(`http://localhost:8000/api/conversations?user_id=${userId}`)
   → Returns: [{id, title, message_count, created_at, updated_at}]
   ```

2. **Send Message:**
   ```javascript
   fetch('http://localhost:8000/chat', {
     method: 'POST',
     body: JSON.stringify({
       message: userInput,
       conversation_id: currentConversationId,
       user_id: userId
     })
   })
   → Message saved to database
   → Title updated if first message
   → refreshHistory triggered
   ```

3. **Load Conversation Messages:**
   ```javascript
   fetch(`http://localhost:8000/api/conversations/${id}/messages`)
   → Returns: [{role, content, timestamp}]
   ```

---

## Dependencies

### Python (Backend):
- `sqlalchemy` - ORM for database operations
- `psycopg2` - PostgreSQL driver
- `fastapi` - API framework
- `pydantic` - Schema validation

### JavaScript (Frontend):
- `react` - UI framework
- `react-markdown` - Markdown rendering in messages
- `lucide-react` - Icons for UI elements

### Database:
- PostgreSQL 18+
- Database name: `smart_irrigation`

---

## Configuration

### Environment Variables (.env):
```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/smart_irrigation
```

### localStorage Keys:
- `smart_farm_user_id` - Unique user identifier

---

## Testing Checklist

After implementing in fresh environment:

- [ ] Database tables created (run `init_chat_db.py`)
- [ ] User ID persists across page reloads
- [ ] Conversations save to database
- [ ] Messages appear in sidebar
- [ ] Titles auto-generate from first message
- [ ] Delete button removes conversations
- [ ] Loading conversation shows messages history
- [ ] Multiple users have isolated conversations

---

## Advantages Over GitHub Version

| Feature | GitHub Repo | Your Version |
|---------|-------------|--------------|
| Chat Persistence | ❌ No | ✅ PostgreSQL |
| Conversation History | ❌ No | ✅ Full Sidebar |
| User Identification | ❌ No | ✅ localStorage |
| Smart Titles | ❌ No | ✅ Auto-generated |
| Multi-conversation | ❌ No | ✅ Unlimited |
| Message History | ❌ No | ✅ Full Retrieval |
| Delete Conversations | ❌ No | ✅ Yes |

---

## Backward Compatibility

**This feature is designed to be optional:**
- If database tables don't exist, chat still works (just not persisted)
- If user ID not in localStorage, new one created
- If conversation_id not provided to /chat, works normally
- No breaking changes to existing functionality

---

## Future Enhancements (Potential)

- Search conversations by keyword
- Archive conversations instead of deleting
- Export conversation history
- Share conversations via unique link
- Conversation tags/categories
- Message editing
- Token usage tracking
- Conversation analytics

---

## Merge Considerations

**When merging with GitHub repository:**

1. **New Files** (will be added):
   - `src/components/ChatHistory.jsx`
   - `src/styles/ChatHistory.css`
   - `backend/init_chat_db.py`

2. **Enhanced Files** (keep your version):
   - `src/pages/Chatbot.jsx` - Has chat history integration
   - `backend/main.py` - Has chat endpoints
   - `backend/models.py` - Has Conversation & Message models
   - `backend/schemas.py` - Has conversation schemas

3. **Database** (manual step):
   - Run `python backend/init_chat_db.py` after merge
   - Creates tables in PostgreSQL

4. **Testing** (after merge):
   - Verify chat history sidebar appears
   - Test creating and deleting conversations
   - Check messages persist across page reloads

---

## Documentation Files

Related documentation:
- `MERGE_PREPARATION.md` - Full merge guide
- `MERGE_SUMMARY.md` - Quick start guide
- `backend/.env.example` - Environment configuration template

---

## Support & Maintenance

**Database Maintenance:**
```sql
-- Check conversation count
SELECT COUNT(*) FROM conversations WHERE user_id = 'your_user_id';

-- Check message count
SELECT COUNT(*) FROM messages;

-- Recent conversations
SELECT id, title, created_at FROM conversations ORDER BY created_at DESC LIMIT 10;

-- Cleanup old conversations (optional)
DELETE FROM conversations WHERE is_archived = TRUE AND created_at < NOW() - INTERVAL '90 days';
```

**Backend Monitoring:**
- Check logs for database connection errors
- Monitor `/api/conversations` endpoint response times
- Verify cascade deletes working properly

---

## Credits

**Implemented By:** Your development team  
**Database:** PostgreSQL 18  
**Backend:** FastAPI + SQLAlchemy  
**Frontend:** React + ReactMarkdown  
**Date:** February 2026  
**Status:** ✅ Production Ready  

---

**This feature represents a significant enhancement to the Smart Farming Assistant chatbot, providing full conversation persistence and user-friendly history management.**
