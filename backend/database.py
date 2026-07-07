from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./chatbot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" or "bot"
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True)  # ml_match, rag+groq, groq_ai
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_chat_message(db, user_id, session_id, role, message, source=None):
    """Save a single chat message to database"""
    chat_entry = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        message=message,
        source=source
    )
    db.add(chat_entry)
    db.commit()
    return chat_entry


def get_chat_history_from_db(db, session_id, user_id=None):
    """Retrieve chat history for a session"""
    query = db.query(ChatHistory).filter(ChatHistory.session_id == session_id)
    
    if user_id:
        query = query.filter(ChatHistory.user_id == user_id)
    
    return query.order_by(ChatHistory.timestamp).all()
