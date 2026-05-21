'use client';

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

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'bot',
      message: 'Hi! I am your AI assistant. How can I help you today?',
      timestamp: getTime(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

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

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const botReply = await sendMessage(text);

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'bot',
      message: botReply,
      timestamp: getTime(),
    };

    setMessages((prev) => [...prev, botMessage]);
    setIsLoading(false);
  };

  return (
    <div className="h-screen flex flex-col bg-[#0f0f1a]">
      <ChatHeader />
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
        {isLoading && (
          <div className="flex gap-3 px-4 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-indigo-300 text-xs font-bold">AI</div>
            <div className="bg-slate-800 px-4 py-3 rounded-2xl rounded-tl-none">
              <div className="flex gap-1 items-center h-4">
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}
