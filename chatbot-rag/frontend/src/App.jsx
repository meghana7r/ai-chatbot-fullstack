import { useState, useRef, useEffect } from "react";
import { sendMessage, uploadDocument, getIndexStats, clearDocuments, clearChat } from "./services/api";

// ── Typing dots ───────────────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div style={s.botRow}>
      <div style={s.avatar}>🤖</div>
      <div style={{ ...s.bubble, ...s.botBubble, display: "flex", gap: 5, alignItems: "center", padding: "12px 16px" }}>
        <span style={s.d1} /><span style={s.d2} /><span style={s.d3} />
      </div>
    </div>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────
function MessageBubble({ msg }) {
  const isUser = msg.role === "user";
  const time = new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return (
    <div style={isUser ? s.userRow : s.botRow}>
      {!isUser && <div style={s.avatar}>🤖</div>}
      <div style={{ maxWidth: "72%" }}>
        <div style={{ ...s.bubble, ...(isUser ? s.userBubble : s.botBubble) }}>
          {msg.content.split("\n").map((line, i, arr) => (
            <span key={i}>{line}{i < arr.length - 1 && <br />}</span>
          ))}
        </div>
        {/* RAG source badge */}
        {msg.sources && msg.sources.length > 0 && (
          <div style={s.sourceBadge}>
            📄 Source: {msg.sources.join(", ")}
          </div>
        )}
        {msg.used_rag === false && msg.role === "bot" && (
          <div style={{ ...s.sourceBadge, background: "#fff8e1", color: "#856404", border: "1px solid #ffc107" }}>
            💡 General knowledge (no document uploaded)
          </div>
        )}
        <div style={{ ...s.timestamp, textAlign: isUser ? "right" : "left" }}>{time}</div>
      </div>
      {isUser && <div style={{ ...s.avatar, background: "#e8d5fb" }}>👤</div>}
    </div>
  );
}

// ── File Upload Panel ─────────────────────────────────────────────────────────
function UploadPanel({ onUpload }) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [stats, setStats] = useState({ documents: [], total_chunks: 0 });
  const fileRef = useRef();

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try { const data = await getIndexStats(); setStats(data); } catch {}
  };

  const handleFile = async (file) => {
    if (!file) return;
    setUploading(true);
    setUploadMsg("");
    try {
      const data = await uploadDocument(file);
      setUploadMsg(`✅ ${data.message} (${data.chunks_created} chunks indexed)`);
      fetchStats();
      onUpload && onUpload(data);
    } catch (err) {
      setUploadMsg(`❌ ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleClearDocs = async () => {
    await clearDocuments();
    setStats({ documents: [], total_chunks: 0 });
    setUploadMsg("🗑️ All documents cleared.");
  };

  return (
    <div style={s.uploadPanel}>
      <h3 style={s.panelTitle}>📁 Document Upload (RAG)</h3>
      <p style={s.panelSub}>Upload PDF, DOCX, or TXT — the AI will answer from your documents</p>

      {/* Drop zone */}
      <div
        style={{ ...s.dropZone, ...(dragging ? s.dropZoneActive : {}) }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
        onClick={() => fileRef.current.click()}
      >
        <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])} />
        {uploading ? (
          <p style={{ color: "#667eea", fontSize: 14 }}>⏳ Processing document...</p>
        ) : (
          <>
            <p style={{ fontSize: 28, margin: "0 0 6px" }}>📂</p>
            <p style={{ fontSize: 13, color: "#888", margin: 0 }}>Drop file here or click to browse</p>
            <p style={{ fontSize: 11, color: "#aaa", margin: "4px 0 0" }}>PDF · DOCX · TXT · max 10MB</p>
          </>
        )}
      </div>

      {/* Upload message */}
      {uploadMsg && <p style={s.uploadMsg}>{uploadMsg}</p>}

      {/* Indexed documents */}
      {stats.documents && stats.documents.length > 0 && (
        <div style={s.statsBox}>
          <p style={s.statsTitle}>📚 Indexed Documents ({stats.total_chunks} chunks)</p>
          {stats.documents.map((doc, i) => (
            <div key={i} style={s.docItem}>📄 {doc}</div>
          ))}
          <button onClick={handleClearDocs} style={s.clearDocsBtn}>🗑️ Clear all documents</button>
        </div>
      )}

      {/* RAG explanation */}
      <div style={s.ragInfo}>
        <p style={s.ragInfoTitle}>How RAG works:</p>
        <p style={s.ragInfoText}>1. You upload a document</p>
        <p style={s.ragInfoText}>2. It gets split into chunks & embedded</p>
        <p style={s.ragInfoText}>3. Stored in FAISS vector database</p>
        <p style={s.ragInfoText}>4. Your question retrieves relevant chunks</p>
        <p style={s.ragInfoText}>5. Groq LLM answers using that context</p>
      </div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState([{
    role: "bot",
    content: "👋 Hello! I'm your AI assistant powered by RAG.\n\nUpload a document on the left and I'll answer questions from it — or just ask me anything!",
    timestamp: Date.now() / 1000,
    used_rag: null,
    sources: []
  }]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef();

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isTyping]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isTyping) return;
    const userMsg = { role: "user", content: trimmed, timestamp: Date.now() / 1000 };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setError("");
    setIsTyping(true);
    try {
      const data = await sendMessage(trimmed, messages);
      setMessages(prev => [...prev, {
        role: "bot",
        content: data.response,
        timestamp: data.timestamp,
        used_rag: data.used_rag,
        sources: data.sources,
        chunks_retrieved: data.chunks_retrieved
      }]);
    } catch {
      setError("⚠️ Cannot reach backend. Make sure it's running on port 8000.");
      setMessages(prev => [...prev, {
        role: "bot", content: "Sorry, I can't connect to the server right now.",
        timestamp: Date.now() / 1000, used_rag: false, sources: []
      }]);
    } finally { setIsTyping(false); }
  };

  const handleClear = async () => {
    await clearChat().catch(() => {});
    setMessages([{ role: "bot", content: "Chat cleared! 🧹 How can I help?", timestamp: Date.now() / 1000, used_rag: null, sources: [] }]);
  };

  return (
    <div style={s.page}>
      {/* Left: Upload Panel */}
      <div style={s.sidebar}>
        <UploadPanel />
      </div>

      {/* Right: Chat */}
      <div style={s.chatArea}>
        {/* Header */}
        <div style={s.header}>
          <div style={s.headerLeft}>
            <span style={{ fontSize: 30 }}>🤖</span>
            <div>
              <h1 style={s.title}>AI Chatbot</h1>
              <p style={s.subtitle}>RAG · FAISS · Groq Llama 3</p>
            </div>
          </div>
          <button onClick={handleClear} style={s.clearBtn}>🗑️ Clear</button>
        </div>

        {error && <div style={s.errorBar}>{error}</div>}

        {/* Messages */}
        <div style={s.chatWindow}>
          {messages.map((msg, i) => <MessageBubble key={i} msg={msg} />)}
          {isTyping && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={s.inputRow}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask anything... (Enter to send)"
            style={s.textarea}
            rows={1}
            disabled={isTyping}
          />
          <button onClick={handleSend} disabled={!input.trim() || isTyping}
            style={{ ...s.sendBtn, opacity: !input.trim() || isTyping ? 0.5 : 1 }}>
            {isTyping ? "..." : "Send ➤"}
          </button>
        </div>
        <p style={s.hint}>Enter to send · Shift+Enter for new line</p>
      </div>

      <style>{`
        @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }
        textarea:focus { border-color:#667eea!important; outline:none; box-shadow:0 0 0 3px rgba(102,126,234,0.15); }
        ::-webkit-scrollbar{width:5px} ::-webkit-scrollbar-thumb{background:#ddd;border-radius:4px}
      `}</style>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const s = {
  page: { display: "flex", minHeight: "100vh", background: "linear-gradient(135deg,#667eea,#764ba2)", padding: 16, gap: 16, fontFamily: "'Segoe UI',system-ui,sans-serif", boxSizing: "border-box" },
  sidebar: { width: 280, flexShrink: 0 },
  chatArea: { flex: 1, display: "flex", flexDirection: "column", minWidth: 0 },
  uploadPanel: { background: "white", borderRadius: 16, padding: 20, height: "100%", boxSizing: "border-box", overflowY: "auto" },
  panelTitle: { margin: "0 0 4px", fontSize: 16, fontWeight: 700, color: "#1a1a2e" },
  panelSub: { margin: "0 0 16px", fontSize: 12, color: "#888" },
  dropZone: { border: "2px dashed #c8d0f5", borderRadius: 12, padding: "24px 16px", textAlign: "center", cursor: "pointer", transition: "all 0.2s", background: "#fafbff" },
  dropZoneActive: { border: "2px dashed #667eea", background: "#f0f3ff" },
  uploadMsg: { fontSize: 12, margin: "10px 0 0", padding: "8px 10px", borderRadius: 8, background: "#f0fff4", color: "#276749" },
  statsBox: { margin: "14px 0 0", padding: 12, background: "#f8f9ff", borderRadius: 10, border: "1px solid #e8ecff" },
  statsTitle: { margin: "0 0 8px", fontSize: 12, fontWeight: 600, color: "#534AB7" },
  docItem: { fontSize: 12, color: "#555", padding: "3px 0", borderBottom: "1px solid #eee" },
  clearDocsBtn: { marginTop: 10, width: "100%", padding: "6px", fontSize: 12, background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 6, cursor: "pointer", color: "#cc0000" },
  ragInfo: { margin: "14px 0 0", padding: 12, background: "#fafafa", borderRadius: 10, border: "1px solid #eee" },
  ragInfoTitle: { margin: "0 0 6px", fontSize: 12, fontWeight: 600, color: "#333" },
  ragInfoText: { margin: "2px 0", fontSize: 11, color: "#888" },
  header: { background: "white", borderRadius: "16px 16px 0 0", padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center" },
  headerLeft: { display: "flex", alignItems: "center", gap: 10 },
  title: { margin: 0, fontSize: 20, fontWeight: 700, color: "#1a1a2e" },
  subtitle: { margin: 0, fontSize: 12, color: "#888" },
  clearBtn: { background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 8, padding: "6px 12px", cursor: "pointer", color: "#cc0000", fontSize: 12 },
  errorBar: { background: "#fff3cd", border: "1px solid #ffc107", color: "#856404", padding: "8px 14px", fontSize: 12 },
  chatWindow: { flex: 1, minHeight: 400, maxHeight: 520, overflowY: "auto", background: "#f8f9fa", padding: "16px 14px", display: "flex", flexDirection: "column", gap: 12 },
  botRow: { display: "flex", justifyContent: "flex-start", alignItems: "flex-end", gap: 8 },
  userRow: { display: "flex", justifyContent: "flex-end", alignItems: "flex-end", gap: 8 },
  avatar: { width: 30, height: 30, borderRadius: "50%", background: "#e0e7ff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0 },
  bubble: { padding: "10px 14px", borderRadius: 16, fontSize: 14, lineHeight: 1.6, wordBreak: "break-word" },
  botBubble: { background: "white", color: "#1a1a2e", border: "1px solid #e0e0e0", borderBottomLeftRadius: 4 },
  userBubble: { background: "linear-gradient(135deg,#667eea,#764ba2)", color: "white", borderBottomRightRadius: 4 },
  sourceBadge: { fontSize: 11, marginTop: 4, padding: "3px 8px", borderRadius: 6, background: "#e8f5e9", color: "#276749", border: "1px solid #c8e6c9", display: "inline-block" },
  timestamp: { fontSize: 10, color: "#aaa", marginTop: 3, paddingLeft: 4, paddingRight: 4 },
  inputRow: { background: "white", borderRadius: "0 0 16px 16px", padding: "12px 14px", display: "flex", gap: 8, alignItems: "center" },
  textarea: { flex: 1, border: "1.5px solid #e0e0e0", borderRadius: 10, padding: "9px 12px", fontSize: 14, fontFamily: "inherit", resize: "none", lineHeight: 1.5 },
  sendBtn: { background: "linear-gradient(135deg,#667eea,#764ba2)", color: "white", border: "none", borderRadius: 10, padding: "9px 18px", fontSize: 14, fontWeight: 600, cursor: "pointer" },
  hint: { color: "rgba(255,255,255,0.65)", fontSize: 11, textAlign: "center", marginTop: 6 },
  d1: { width: 7, height: 7, borderRadius: "50%", background: "#667eea", display: "inline-block", animation: "bounce 1.2s 0s infinite" },
  d2: { width: 7, height: 7, borderRadius: "50%", background: "#764ba2", display: "inline-block", animation: "bounce 1.2s 0.2s infinite" },
  d3: { width: 7, height: 7, borderRadius: "50%", background: "#667eea", display: "inline-block", animation: "bounce 1.2s 0.4s infinite" },
};
