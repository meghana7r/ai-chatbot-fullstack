````md
# AI Chatbot Backend

Backend service for the AI Chatbot internship project built using FastAPI.

---

## Features

- FastAPI backend setup
- REST API endpoints
- Frontend-backend integration
- Intelligent chatbot replies
- Empty message validation
- Chatbot memory feature
- Request logging
- Swagger API documentation
- Health monitoring endpoint
- Timestamp-based responses

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

---

## Project Structure

```text
backend/
├── main.py
├── requirements.txt
├── routes/
│   ├── __init__.py
│   └── chat.py
└── README.md
````

---

## API Endpoints

### Home Endpoint

```http
GET /
```

### Health Check Endpoint

```http
GET /health
```

### Chat Endpoint

```http
POST /chat
```

### Example Request

```json
{
  "message": "Hello"
}
```

### Example Response

```json
{
  "status": "success",
  "timestamp": "15:00:00",
  "user_message": "Hello",
  "bot_reply": "Hello! How can I help you today?"
}
```

---

## Run Backend

### Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### Run Server

```bash
python3 -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Developer

Amrutha Varshini — Backend Developer Intern

```
```
