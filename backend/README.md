# AI Chatbot — Backend
**Developer: Amrutha Varshini**
**Stack: Python · FastAPI · FAISS · Groq (Llama 3) · SentenceTransformers**

---

## Folder Structure
```
backend/
├── main.py                 ← FastAPI app entry point + CORS
├── rag_engine.py           ← FAISS vector DB + Groq LLM + RAG pipeline
├── document_processor.py  ← PDF / DOCX / TXT text extraction
├── requirements.txt        ← Python dependencies
├── .env                    ← API keys (never commit this!)
├── .gitignore
└── routes/
    ├── chat.py             ← POST /api/chat
    ├── upload.py           ← POST /api/upload
    └── health.py           ← GET /health
```

---

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Add your Groq API key to `.env` before running.

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /health | Backend health check |
| POST | /api/chat | Send message, get RAG response |
| POST | /api/upload | Upload PDF/DOCX/TXT to FAISS |
| GET | /api/upload/stats | View indexed documents |
| DELETE | /api/upload/clear | Clear all documents |
| DELETE | /api/chat/clear | Clear chat |

API docs auto-available at: **http://localhost:8000/docs**

---

## RAG Pipeline
1. User uploads document → text extracted → split into chunks
2. Chunks embedded using SentenceTransformer → stored in FAISS
3. User asks question → question embedded → FAISS finds similar chunks
4. Relevant chunks + question sent to Groq LLM → AI answer returned
5. If question is unrelated to document → answers from general knowledge
