// api.ts — connects frontend to MegaBot backend
// Built by Meghana Ravi
// Sends full conversation history so MegaBot remembers context!

export async function sendMessage(
  message: string,
  history: { role: string; message: string }[] = []
): Promise<string> {
  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    });
    if (!response.ok) throw new Error('Backend error');
    const data = await response.json();
    return data.bot_reply;
  } catch (error) {
    return 'Sorry, I could not connect to the server. Please try again.';
  }
}
