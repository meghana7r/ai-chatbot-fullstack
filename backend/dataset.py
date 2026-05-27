# Predefined Question & Answer Dataset
# This is used for rule-based keyword matching (Week 2 task)

QA_DATASET = [
    {
        "keywords": ["hello", "hi", "hey", "greetings"],
        "response": "Hello! 👋 I'm your AI assistant. How can I help you today?"
    },
    {
        "keywords": ["how are you", "how do you do", "how's it going"],
        "response": "I'm doing great, thanks for asking! Ready to help you. 😊"
    },
    {
        "keywords": ["bye", "goodbye", "see you", "take care"],
        "response": "Goodbye! Have a wonderful day! 👋"
    },
    {
        "keywords": ["thank", "thanks", "thank you"],
        "response": "You're welcome! Is there anything else I can help you with?"
    },
    {
        "keywords": ["name", "who are you", "what are you"],
        "response": "I'm an AI Chatbot built with FastAPI and React!"
    },
    {
        "keywords": ["help", "support", "what can you do"],
        "response": "I can answer your questions and have conversations with you!"
    },
    {
        "keywords": ["python", "programming", "code", "coding"],
        "response": "Python is a great language! It's widely used in data science and AI."
    },
    {
        "keywords": ["machine learning", "ml", "artificial intelligence", "ai", "deep learning"],
        "response": "Machine Learning and AI are fascinating fields! This chatbot uses Groq's Llama 3 AI model."
    },
    {
        "keywords": ["data science", "data analyst", "statistics", "data"],
        "response": "Data Science is all about extracting insights from data using Python, Pandas, and ML!"
    },
    {
        "keywords": ["fastapi", "api", "backend", "server"],
        "response": "FastAPI is a modern Python web framework. This chatbot's backend is built with FastAPI!"
    },
    {
        "keywords": ["react", "frontend", "javascript", "nextjs"],
        "response": "React is a popular JavaScript library for building user interfaces!"
    },
    {
        "keywords": ["joke", "funny", "laugh", "humor"],
        "response": "Why do programmers prefer dark mode? Because light attracts bugs! 🐛😄"
    },
    {
        "keywords": ["internship", "intern", "project", "company"],
        "response": "Internships are great for gaining real world experience. Good luck with your project!"
    },
    {
        "keywords": ["groq", "llama", "llm", "language model"],
        "response": "Groq provides fast AI inference using Llama 3 — the AI model powering this chatbot!"
    },
    {
        "keywords": ["weather", "temperature", "rain", "sunny"],
        "response": "I don't have real-time weather data. Please check a weather app!"
    },
    {
        "keywords": ["time", "date", "today"],
        "response": "I don't have access to real-time data. Please check your device clock!"
    },
    {
        "keywords": ["study", "learn", "tutorial", "resources"],
        "response": "Great resources: Python → docs.python.org, FastAPI → fastapi.tiangolo.com, React → react.dev"
    },
]

# Default response when no keyword matches
DEFAULT_RESPONSE = None  # None means → ask Groq AI instead
