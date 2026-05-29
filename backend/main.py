from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat,info

app = FastAPI(
    title="AI Chatbot API",
    description="Simple AI Chatbot using keyword matching + Groq LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router, prefix="/api")
app.include_router(info.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
