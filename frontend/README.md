# MegaBot — AI Chatbot

A full-stack AI chatbot application built with Next.js, TypeScript, and Tailwind CSS.

**Live Demo:** https://delicate-sherbet-ee7890.netlify.app

## Built By
Meghana Ravi — Frontend Developer

## Tech Stack
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python, Groq LLM, FAISS
- **Deployment:** Netlify (Frontend), Render (Backend)

## Features
- Real-time AI chat powered by Groq LLM
- RAG-based document Q&A (PDF, DOCX, TXT upload)
- Chat history with localStorage persistence
- Session management with unique session IDs
- File upload with size and type validation
- Mobile responsive design
- Error handling for network, server, and timeout failures

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

```
NEXT_PUBLIC_BACKEND_URL=your_backend_url
```
