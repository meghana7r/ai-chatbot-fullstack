const BASE_URL = "http://localhost:8000/api";

// Send message to RAG chatbot
export async function sendMessage(message, chatHistory = []) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, chat_history: chatHistory }),
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

// Upload a document to FAISS
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

// Get FAISS index stats
export async function getIndexStats() {
  const res = await fetch(`${BASE_URL}/upload/stats`);
  return res.json();
}

// Clear all documents
export async function clearDocuments() {
  const res = await fetch(`${BASE_URL}/upload/clear`, { method: "DELETE" });
  return res.json();
}

// Clear chat
export async function clearChat() {
  const res = await fetch(`${BASE_URL}/chat/clear`, { method: "DELETE" });
  return res.json();
}

// Health check
export async function checkHealth() {
  const res = await fetch("http://localhost:8000/health");
  return res.json();
}
