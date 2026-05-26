from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import chat, upload, health
from rag_engine import load_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load existing FAISS index on startup
    print("Starting AI Chatbot RAG Backend...")
    load_index()
    yield
    print("Shutting down...")


app = FastAPI(
    title="AI Chatbot RAG API",
    description="Chatbot with RAG using FAISS + Groq LLM",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
