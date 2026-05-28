# Predefined Question & Answer Dataset

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
        "keywords": ["thank you", "thanks a lot", "thank you so much"],
        "response": "You're welcome! Is there anything else I can help you with?"
    },
    {
        "keywords": ["who are you", "what are you", "your name"],
        "response": "I'm an AI Chatbot built with FastAPI and React!"
    },
    {
        "keywords": ["what can you do", "how can you help"],
        "response": "I can answer your questions and have conversations with you!"
    },
    {
        "keywords": ["tell me a joke", "say a joke", "make me laugh"],
        "response": "Why do programmers prefer dark mode? Because light attracts bugs! 🐛😄"
    },
]

# None means → ask Groq AI instead
DEFAULT_RESPONSE = None
