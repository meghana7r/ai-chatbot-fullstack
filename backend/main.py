# main.py — MegaBot Backend Entry Point
# Built by Meghana Ravi
# Starts the FastAPI server and loads environment variables

from dotenv import load_dotenv
load_dotenv()  # Load .env file FIRST before anything else

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/")
def home():
    return {"message": "MegaBot backend is running!"}

@app.get("/health")
def health():
    return {"status": "success", "message": "Backend is running properly"}
