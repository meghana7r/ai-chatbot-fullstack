'use client';
// chat/page.tsx — The main chat window
// Built by Meghana Ravi
// Week 3: Added sidebar for chat history + responsive mobile design

import { useState, useRef, useEffect } from 'react';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';
import ChatHeader from '../components/ChatHeader';
import { sendMessage } from '../utils/api';

type Message = {
  id: string;
  role: 'user' | 'bot';
  message: string;
  timestamp: string;
};

// ChatSession — each saved session in the sidebar history
type ChatSession = {
  id: string;
  title: string;       // first user message as title
  date: string;        // when it was saved
  messages: Message[]; // full message list
};

function getTime() {
  return new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function getDate() {
  return new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
}

export default function ChatPage() {
  // Current chat messages
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'bot',
      message: 'Hi! I am MegaBot, your smart AI assistant. How can I help you today? ✨',
      timestamp: getTime(),
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);

  // Sidebar — stores all previous chat sessions
  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);

  // Controls sidebar open/close on mobile
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  // messageCount — counts only user messages, shown in the header
  const messageCount = messages.filter((m) => m.role === 'user').length;

  // Auto-scroll to bottom whenever new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // handleSend — adds user message, calls API, adds bot reply
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

    const botReply = await sendMessage(text, updatedMessages);

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'bot',
      message: botReply,
      timestamp: getTime(),
    };

    setMessages((prev) => [...prev, botMessage]);
    setIsLoading(false);
  };

  // handleClear — saves current chat to history before clearing
  const handleClear = () => {
    // Only save to history if there are user messages
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

    // Reset to welcome message
    setMessages([{
      id: '1',
      role: 'bot',
      message: 'Chat cleared! 🧹 Hi, I am MegaBot — how can I help?',
      timestamp: getTime(),
    }]);
  };

  // loadSession — loads a previous chat from sidebar
  const loadSession = (session: ChatSession) => {
    setMessages(session.messages);
    setSidebarOpen(false); // close sidebar on mobile after selecting
  };

  // deleteSession — removes a session from history
  const deleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setChatHistory((prev) => prev.filter((s) => s.id !== id));
  };

  return (
    <div className="h-screen flex bg-[#fff8f5] overflow-hidden">

      {/* ── Sidebar — chat history ── */}
      {/* On desktop: always visible. On mobile: slides in when sidebarOpen is true */}
      <div className={`
        fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-orange-100 flex flex-col transition-transform duration-300
        md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Sidebar header */}
        <div className="px-4 py-4 border-b border-orange-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🌸</span>
            <span className="text-slate-700 font-semibold text-sm">Chat History</span>
          </div>
          {/* Close button — only visible on mobile */}
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-slate-400 hover:text-rose-500 text-lg"
          >
            ✕
          </button>
        </div>

        {/* New Chat button */}
        <div className="px-3 py-3 border-b border-orange-100">
          <button
            onClick={handleClear}
            className="w-full py-2 rounded-xl bg-gradient-to-r from-rose-500 to-orange-500 text-white text-xs font-semibold hover:opacity-90 transition-all"
          >
            + New Chat
          </button>
        </div>

        {/* Session list */}
        <div className="flex-1 overflow-y-auto py-2">
          {chatHistory.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <p className="text-slate-300 text-xs">No chat history yet.</p>
              <p className="text-slate-300 text-xs mt-1">Start chatting to save sessions!</p>
            </div>
          ) : (
            chatHistory.map((session) => (
              <div
                key={session.id}
                onClick={() => loadSession(session)}
                className="group mx-2 mb-1 px-3 py-2.5 rounded-xl cursor-pointer hover:bg-rose-50 transition-all flex items-start justify-between gap-2"
              >
                <div className="flex-1 min-w-0">
                  {/* Session title — first message */}
                  <p className="text-slate-700 text-xs font-medium truncate">{session.title}</p>
                  {/* Session date */}
                  <p className="text-slate-400 text-[10px] mt-0.5">{session.date}</p>
                </div>
                {/* Delete button — appears on hover */}
                <button
                  onClick={(e) => deleteSession(session.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-rose-400 text-xs transition-all flex-shrink-0"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>

        {/* Sidebar footer */}
        <div className="px-4 py-3 border-t border-orange-100">
          <p className="text-slate-300 text-[10px] text-center">Built by Meghana Ravi</p>
        </div>
      </div>

      {/* Mobile overlay — clicking it closes sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Main chat area ── */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Header — passes onClear and onMenuClick for mobile sidebar toggle */}
        <ChatHeader
          messageCount={messageCount}
          onClear={handleClear}
          onMenuClick={() => setSidebarOpen(true)}
        />

        {/* Scrollable message area */}
        <div className="flex-1 overflow-y-auto bg-[#fff8f5] px-4 py-4">
          <MessageList messages={messages} />

          {/* Typing indicator */}
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

        {/* Input bar */}
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
