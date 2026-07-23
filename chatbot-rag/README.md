# AI Chatbot with RAG — Complete Setup Guide

## Tech Stack
- **LLM**: Groq (Llama 3) — free, fast
- **Vector DB**: FAISS (by Meta) — runs locally, no account needed
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2) — free, local
- **Backend**: Python FastAPI
- **Frontend**: React + Vite

---

## Step 1 — Add your Groq API Key

Open `backend/.env` and replace the placeholder:
```
GROQ_API_KEY=your_groq_api_key_here
```
↓ becomes ↓
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```
Get your free key at: https://console.groq.com

---

## Step 2 — Run the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install packages (first time takes 2-3 mins - downloads embedding model)
pip install -r requirements.txt

# Start the server
python main.py
```

Visit http://localhost:8000/docs to see all API endpoints.

---

## Step 3 — Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## How to Use

1. Upload a PDF/DOCX/TXT file using the left panel
2. Ask questions about your document in the chat
3. The AI answers using your document (RAG) — you'll see the source shown below each reply

---

## RAG Flow (How it works)

```
User uploads PDF
      ↓
Extract text (pypdf / python-docx)
      ↓
Split into 500-char chunks (LangChain splitter)
      ↓
Embed each chunk → 384-dim vectors (SentenceTransformer)
      ↓
Store vectors in FAISS index (saved to disk)
      ↓
User asks a question
      ↓
Embed the question → search FAISS → get top 4 similar chunks
      ↓
Build prompt: [System: here is the context...] + [User: question]
      ↓
Send to Groq (Llama 3) → get AI answer
      ↓
Return answer + source filename to frontend
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /health | Check backend status |
| POST | /api/chat | Send message, get RAG response |
| POST | /api/upload | Upload document to FAISS |
| GET | /api/upload/stats | See indexed documents |
| DELETE | /api/upload/clear | Clear all documents |
| DELETE | /api/chat/clear | Clear chat |

---

## Project Structure

```
chatbot-rag/
├── backend/
│   ├── main.py               ← FastAPI app entry point
│   ├── rag_engine.py         ← FAISS + Groq RAG pipeline
│   ├── document_processor.py ← PDF/DOCX/TXT text extraction
│   ├── requirements.txt
│   ├── .env                  ← YOUR API KEY GOES HERE
│   └── routes/
│       ├── chat.py           ← POST /api/chat
│       ├── upload.py         ← POST /api/upload
│       └── health.py         ← GET /health
└── frontend/
    ├── src/
    │   ├── App.jsx            ← Full chat UI + upload panel
    │   ├── main.jsx
    │   └── services/api.js    ← All fetch calls to backend
    ├── package.json
    └── vite.config.js
```
