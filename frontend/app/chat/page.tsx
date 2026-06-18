'use client';
// chat/page.tsx — The main chat window
// Built by Meghana Ravi
// Week 4: API error handling | Week 5: localStorage | Week 6: Document upload section
// Removed backend health check banner since backend has no /health route

import { useState, useRef, useEffect } from 'react';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';
import ChatHeader from '../components/ChatHeader';
import DocumentUpload from '../components/DocumentUpload';
import { sendMessage, ApiError } from '../utils/api';

type Message = {
  id: string;
  role: 'user' | 'bot';
  message: string;
  timestamp: string;
};

type ChatSession = {
  id: string;
  title: string;
  date: string;
  messages: Message[];
};

function getTime() {
  return new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function getDate() {
  return new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
}

const STORAGE_KEY = 'megabot_chat_history';

const ERROR_MESSAGES: Record<string, string> = {
  network: '⚠️ Cannot reach MegaBot server. Make sure the backend is running on port 8000.',
  server: '⚠️ MegaBot server returned an error. Please try again.',
  timeout: '⚠️ MegaBot is taking too long to respond. Please try again.',
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'bot',
      message: 'Hi! I am MegaBot, your smart AI assistant. How can I help you today? ✨',
      timestamp: getTime(),
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiError, setApiError] = useState<ApiError>(null);

  const [chatHistory, setChatHistory] = useState<ChatSession[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const bottomRef = useRef<HTMLDivElement>(null);
  const messageCount = messages.filter((m) => m.role === 'user').length;

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
    } catch {
      console.error('Could not save chat history to localStorage');
    }
  }, [chatHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      message: text,
      timestamp: getTime(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);
    setApiError(null);

    const { reply, error } = await sendMessage(
      text,
      updatedMessages.map((m) => ({ role: m.role, message: m.message }))
    );

    if (error) {
      setApiError(error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        message: ERROR_MESSAGES[error],
        timestamp: getTime(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } else {
      setApiError(null);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        message: reply,
        timestamp: getTime(),
      };
      setMessages((prev) => [...prev, botMessage]);
    }

    setIsLoading(false);
  };

  const handleClear = () => {
    const userMessages = messages.filter((m) => m.role === 'user');
    if (userMessages.length > 0) {
      const session: ChatSession = {
        id: Date.now().toString(),
        title: userMessages[0].message.slice(0, 40) + (userMessages[0].message.length > 40 ? '...' : ''),
        date: getDate(),
        messages: messages,
      };
      setChatHistory((prev) => [session, ...prev]);
    }

    setMessages([{
      id: '1',
      role: 'bot',
      message: 'Chat cleared! 🧹 Hi, I am MegaBot — how can I help?',
      timestamp: getTime(),
    }]);
    setApiError(null);
  };

  const loadSession = (session: ChatSession) => {
    setMessages(session.messages);
    setSidebarOpen(false);
  };

  const deleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setChatHistory((prev) => prev.filter((s) => s.id !== id));
  };

  const deleteAllHistory = () => {
    setChatHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div className="h-screen flex bg-[#fff8f5] overflow-hidden">

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-orange-100 flex flex-col transition-transform duration-300
        md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="px-4 py-4 border-b border-orange-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🌸</span>
            <span className="text-slate-700 font-semibold text-sm">Chat History</span>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="md:hidden text-slate-400 hover:text-rose-500 text-lg">✕</button>
        </div>

        <div className="px-3 py-3 border-b border-orange-100">
          <button
            onClick={handleClear}
            className="w-full py-2 rounded-xl bg-gradient-to-r from-rose-500 to-orange-500 text-white text-xs font-semibold hover:opacity-90 transition-all"
          >
            + New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          {chatHistory.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <p className="text-slate-300 text-xs">No chat history yet.</p>
              <p className="text-slate-300 text-xs mt-1">Start chatting to save sessions!</p>
            </div>
          ) : (
            <>
              {chatHistory.map((session) => (
                <div
                  key={session.id}
                  onClick={() => loadSession(session)}
                  className="group mx-2 mb-1 px-3 py-2.5 rounded-xl cursor-pointer hover:bg-rose-50 transition-all flex items-start justify-between gap-2"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-700 text-xs font-medium truncate">{session.title}</p>
                    <p className="text-slate-400 text-[10px] mt-0.5">{session.date}</p>
                  </div>
                  <button
                    onClick={(e) => deleteSession(session.id, e)}
                    className="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-rose-400 text-xs transition-all flex-shrink-0"
                  >
                    🗑️
                  </button>
                </div>
              ))}
              <div className="px-3 mt-2">
                <button
                  onClick={deleteAllHistory}
                  className="w-full py-1.5 rounded-xl border border-rose-200 text-rose-400 text-xs hover:bg-rose-50 transition-all"
                >
                  🗑️ Clear all history
                </button>
              </div>
            </>
          )}
        </div>

        {/* Week 6 — Document upload section for RAG */}
        <DocumentUpload />

        <div className="px-4 py-3 border-t border-orange-100">
          <p className="text-slate-300 text-[10px] text-center">Built by Meghana Ravi</p>
        </div>
      </div>

      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-20 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatHeader
          messageCount={messageCount}
          onClear={handleClear}
          onMenuClick={() => setSidebarOpen(true)}
        />

        {apiError && (
          <div className="bg-orange-50 border-b border-orange-200 px-4 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-orange-500 text-xs">⚠️</span>
              <p className="text-orange-700 text-xs font-medium">{ERROR_MESSAGES[apiError]}</p>
            </div>
            <button onClick={() => setApiError(null)} className="text-orange-400 hover:text-orange-600 text-xs ml-4">✕</button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto bg-[#fff8f5] px-4 py-4">
          <MessageList messages={messages} />

          {isLoading && (
            <div className="flex gap-3 px-2 mb-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-rose-500 to-orange-400 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                M
              </div>
              <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none border border-orange-200 shadow-sm">
                <div className="flex gap-1 items-center h-4">
                  <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
