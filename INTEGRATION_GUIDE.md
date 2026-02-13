# Backend + Frontend Integration Summary

## Architecture

```
React Chatbot (localhost:5173)
         ↓ (HTTP POST)
FastAPI Backend (localhost:8000)
         ↓ (Bearer Token)
Hugging Face Inference API
         ↓
soumak/agri_gemma3 Model
         ↓
Generated Response (agriculture-focused)
```

## What Was Created

### Backend (FastAPI)
- **backend/main.py** - FastAPI server with `/chat` endpoint
- **backend/requirements.txt** - Python dependencies
- **backend/.env** - Environment config (HF_API_KEY)

### Frontend (React)
- **src/pages/Chatbot.jsx** - Updated to call FastAPI backend instead of hardcoded responses

## How It Works

1. User types message in Chatbot page
2. Frontend sends request to `http://localhost:8000/chat`
3. Backend receives message + context
4. Backend calls Hugging Face model with Bearer token
5. Model generates agriculture-specific response
6. Response sent back to frontend
7. Chatbot displays reply

## Setup Steps

1. **Get Hugging Face API Key**
   - https://huggingface.co/settings/tokens
   - Create read-only token

2. **Configure Backend**
   ```bash
   cd backend
   # Edit .env with your HF_API_KEY
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Backend**
   ```bash
   uvicorn main:app --reload
   ```

5. **Backend Ready**
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs
   - Chat endpoint: http://localhost:8000/chat

6. **Frontend Already Integrated**
   - No changes needed to frontend
   - Chatbot automatically connects to backend
   - Just start dev server as usual: `npm run dev`

## Key Features

✅ Context-aware responses (location, weather, crop, soil)
✅ Farmer-friendly language
✅ HF API key never exposed to frontend
✅ CORS enabled for localhost:5173
✅ Error handling with fallback messages
✅ Loading state while waiting for model
✅ Health check endpoint

## Testing

### Test Backend Directly
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How to improve crop yield?", "context": "Crop: Wheat"}'
```

### Test Frontend
- Open localhost:5173/chatbot
- Type a farming question
- Should get response from HF model within 5-10 seconds

## Environment Variables

Only **HF_API_KEY** is required in backend/.env

Never commit .env to git!

## Security

- HF API key stored only in backend/.env
- Frontend cannot access API key
- Backend validates requests before calling HF
- CORS restricted to localhost:5173
