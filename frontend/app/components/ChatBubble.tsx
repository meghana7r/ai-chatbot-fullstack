'use client';

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
      <div className={`max-w-[70%] ${role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
          ${role === 'user'
            ? 'bg-indigo-600 text-white rounded-tr-none'
            : 'bg-slate-800 text-slate-200 rounded-tl-none'
          }`}>
          {message}
        </div>
        <span className="text-xs text-slate-500">{timestamp}</span>
      </div>
    </div>
  );
}


