from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
import uvicorn
app = FastAPI(title="MegaBot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)