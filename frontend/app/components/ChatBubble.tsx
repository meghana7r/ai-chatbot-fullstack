'use client';

// ChatBubble.tsx — Individual chat message bubble
// Built by Meghana Ravi
// Renders bullet points, numbered lists, and line breaks from AI properly

import Avatar from './Avatar';

type ChatBubbleProps = {
  role: 'user' | 'bot';
  message: string;
  timestamp: string;
};

export default function ChatBubble({ role, message, timestamp }: ChatBubbleProps) {
  return (
    <div className={`flex gap-3 mb-4 ${role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
      <Avatar role={role} />
      <div className={`max-w-[70%] flex flex-col gap-1 ${role === 'user' ? 'items-end' : 'items-start'}`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
          ${role === 'user'
            ? 'bg-gradient-to-br from-rose-500 to-orange-400 text-white rounded-tr-none shadow-md shadow-orange-200'
            : 'bg-rose-50 text-slate-700 rounded-tl-none border border-rose-100 shadow-sm'
          }`}>
          {message.split('\n').map((line, index) => (
            <span key={index}>
              {line}
              {index < message.split('\n').length - 1 && <br />}
            </span>
          ))}
        </div>
        <span className="text-xs text-slate-400">{timestamp}</span>
      </div>
    </div>
  );
}
