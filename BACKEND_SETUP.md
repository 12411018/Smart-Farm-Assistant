# Smart Farming Assistant - Backend Setup Guide

## Quick Start

### 1️⃣ Get Hugging Face API Key
- Go to: https://huggingface.co/settings/tokens
- Create a new token (read access is fine)
- Copy the token

### 2️⃣ Setup Backend Environment

```bash
cd backend
```

Create a `.env` file (or update existing):
```
HF_API_KEY=hf_your_token_here
```

Replace `hf_your_token_here` with your actual token.

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install fastapi uvicorn python-dotenv requests
```

### 4️⃣ Run FastAPI Server

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5️⃣ Verify Backend is Working

Open browser to: http://localhost:8000/health

Expected response:
```json
{"status": "ok"}
```

### 6️⃣ View API Documentation

Open: http://localhost:8000/docs

(Swagger UI will show all endpoints)

### 7️⃣ Test Chat Endpoint

Use Swagger at http://localhost:8000/docs or curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I improve wheat yield?",
    "context": "Location: Pune, Crop: Wheat"
  }'
```

## Frontend Integration

The Chatbot page automatically connects to FastAPI on:
```
http://localhost:8000/chat
```

No additional setup needed in frontend.

## Troubleshooting

### "Connection error" in Chatbot
- Make sure FastAPI is running: `uvicorn main:app --reload`
- Check that backend is on `http://localhost:8000`

### "Model error" response
- Verify HF_API_KEY is correct in `backend/.env`
- Check token has permission to access soumak/agri_gemma3 model

### CORS errors
- Frontend runs on `http://localhost:5173`
- Backend allows this in main.py CORSMiddleware

## Model Info

- **Model**: soumak/agri_gemma3
- **Type**: Text generation
- **Task**: Agriculture-focused instruction following
- **API**: Hugging Face Inference API

## Stop Backend

Press `Ctrl+C` in terminal running FastAPI.
