# AI Chatbot Backend

An internship project — a backend service for an AI chatbot built using FastAPI FastAPI and Python.

---

# Tech Stack

**Framework:** FastAPI

**Language:** Python

**Server:** Uvicorn

**Validation:** Pydantic

**API Type:** REST API

---

# Features

* FastAPI backend setup
* Chatbot API development
* POST request handling
* Request validation using Pydantic
* Frontend-backend integration
* CORS enabled
* Swagger API documentation
* Modular route architecture

---

# Getting Started

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run development server

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

# Project Structure

```text
Backend/
├── main.py
├── requirements.txt
├── .gitignore
├── routes/
│   ├── __init__.py
│   └── chat.py
└── venv/
```

---

# API Endpoints

## Home Route

```http
GET /
```

---

## Health Check Route

```http
GET /health
```

---

## Chat API

```http
POST /chat
```

Request Body:

```json
{
  "message": "Hello AI"
}
```

---

# Frontend Connection

Frontend connects using:

```text
POST http://127.0.0.1:8000/chat
```

CORS enabled for:

```text
http://localhost:3000
```

---

# Week Progress

✅ Day 1 — Backend setup, FastAPI server, API routes

✅ Day 2 — Chat API, frontend-backend integration, route organization

⬜ Day 3 — AI integration

⬜ Day 4 — Testing and deployment

---

# Developer

Amrutha Varshini — Backend Developer Intern
