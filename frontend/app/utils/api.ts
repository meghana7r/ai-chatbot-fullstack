

const BACKEND_URL = 'http://127.0.0.1:8000';

export type ApiError = 'network' | 'server' | 'timeout' | null;

// Generate unique session ID for each chat session
export const generateSessionId = (): string => {
  return `chat_${Date.now()}_${Math.random().toString(36).substring(7)}`;
};

export async function sendMessage(
  message: string,
  history: { role: string; message: string }[] = [],
  sessionId: string = 'default'
): Promise<{ reply: string; error: ApiError }> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${BACKEND_URL}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        history,
        session_id: sessionId,
      }),
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

// Upload document with session_id
export async function uploadDocument(
  file: File,
  sessionId: string
): Promise<{ success: boolean; message: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${BACKEND_URL}/chat/upload?session_id=${sessionId}`,
      { method: 'POST', body: formData }
    );

    const data = await response.json();

    if (!response.ok) {
      return { success: false, message: data.detail || 'Upload failed' };
    }

    return { success: true, message: data.message || 'Document uploaded successfully!' };

  } catch {
    return { success: false, message: 'Could not reach the server. Make sure backend is running.' };
  }
}

// Fetch document list for a session
export async function fetchDocuments(sessionId: string): Promise<{
  documents: { name: string; chunks: number; is_current: boolean }[];
  current_document: string | null;
}> {
  try {
    const response = await fetch(`${BACKEND_URL}/chat/documents/${sessionId}`);
    const data = await response.json();

    if (data.status === 'success') {
      return {
        documents: data.documents || [],
        current_document: data.current_document || null,
      };
    }
    return { documents: [], current_document: null };
  } catch {
    return { documents: [], current_document: null };
  }
}

// Delete a single document from a session
export async function deleteDocument(
  sessionId: string,
  docName: string
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(
      `${BACKEND_URL}/chat/delete-file/${sessionId}/${encodeURIComponent(docName)}`,
      { method: 'DELETE' }
    );

    const data = await response.json();

    if (!response.ok) {
      return { success: false, message: data.detail || 'Delete failed' };
    }

    return { success: true, message: data.message || 'File deleted successfully' };
  } catch {
    return { success: false, message: 'Could not reach the server.' };
  }
}

// Clear session when switching/closing chat
export async function clearSession(sessionId: string): Promise<void> {
  try {
    await fetch(`${BACKEND_URL}/chat/clear-session/${sessionId}`, { method: 'POST' });
  } catch {
    // fail silently
  }
}