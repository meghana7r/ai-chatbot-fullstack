from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, health

# Create FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="Simple AI Chatbot using keyword matching + Groq LLM",
    version="1.0.0"
)

# Allow React frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React runs on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(chat.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
