'use client';

// ChatBubble.tsx — Individual chat message bubble
// Built by Meghana Ravi
// User bubbles: orange/rose gradient. Bot bubbles: clean white with orange border.

import Avatar from './Avatar';

type ChatBubbleProps = {
  role: 'user' | 'bot';
  message: string;
  timestamp: string;
};

export default function ChatBubble({ role, message, timestamp }: ChatBubbleProps) {
  return (
    // Flex row — user messages on right, bot messages on left
    <div className={`flex gap-3 mb-4 ${role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

      {/* Avatar — M for MegaBot, U for user */}
      <Avatar role={role} />

      <div className={`max-w-[70%] flex flex-col gap-1 ${role === 'user' ? 'items-end' : 'items-start'}`}>

        {/* Bubble — orange/rose gradient for user, clean white for bot */}
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
          ${role === 'user'
            ? 'bg-gradient-to-br from-rose-500 to-orange-400 text-white rounded-tr-none shadow-md shadow-orange-200'
            : 'bg-white text-slate-700 rounded-tl-none border border-orange-100 shadow-sm'
          }`}>
          {message}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-slate-400">{timestamp}</span>
      </div>
    </div>
  );
}
