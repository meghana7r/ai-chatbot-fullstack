// api.ts — connects frontend to MegaBot backend
// Built by Meghana Ravi
// Week 4: API error handling | Week 6: RAG document upload

const BACKEND_URL = 'http://127.0.0.1:8000';

export type ApiError = 'network' | 'server' | 'timeout' | null;

export async function sendMessage(
  message: string,
  history: { role: string; message: string }[] = []
): Promise<{ reply: string; error: ApiError }> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      return { reply: '', error: 'server' };
    }

    const data = await response.json();
    return { reply: data.bot_reply, error: null };

  } catch (error: any) {
    if (error.name === 'AbortError') {
      return { reply: '', error: 'timeout' };
    }
    return { reply: '', error: 'network' };
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, { method: 'GET' });
    return response.ok;
  } catch {
    return false;
  }
}

// uploadDocument — Week 6: sends a file to the RAG backend for indexing
export async function uploadDocument(
  file: File
): Promise<{ success: boolean; message: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${BACKEND_URL}/rag/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      return { success: false, message: data.detail || 'Upload failed' };
    }

    return { success: true, message: data.message || 'Document uploaded successfully!' };

  } catch (error) {
    return { success: false, message: 'Could not reach the server. Make sure backend is running.' };
  }
}
