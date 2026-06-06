# main.py — MegaBot Backend Entry Point
# Built by Meghana Ravi
# Starts the FastAPI server and loads environment variables

from dotenv import load_dotenv
load_dotenv()  # Load .env file FIRST before anything else

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, nlp

app = FastAPI(
    title="AI Chatbot API",
    description="AI Chatbot using keyword matching + NLP + Groq LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(nlp.router)

@app.get("/")
def home():
    return {"message": "MegaBot backend is running!"}

@app.get("/health")
def health():
    return {"status": "success", "message": "Backend is running properly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    