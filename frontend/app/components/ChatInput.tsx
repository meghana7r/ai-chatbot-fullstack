import { useState } from 'react';

// ChatInput.tsx — Message input bar at the bottom
// Built by Meghana Ravi
// Clean light theme — white input box, dark orange Send button

type ChatInputProps = {
  onSend: (message: string) => void;
  isLoading: boolean;
};

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  // input — tracks what the user is currently typing
  const [input, setInput] = useState('');

  // handleSend — sends message if not empty and bot is not loading
  const handleSend = () => {
    if (input.trim() === '' || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  // handleKeyDown — Enter sends, Shift+Enter adds new line
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    // Input bar — orange tinted background with solid orange top border
    <div className="border-t-2 border-orange-500 px-4 py-4 bg-orange-50 shadow-md">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">

        {/* Text area — white background, solid orange border, dark readable text */}
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
          rows={1}
          className="flex-1 resize-none bg-white text-slate-800 placeholder-slate-500 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-orange-500 border-2 border-orange-500 shadow-sm"
        />

        {/* Send button — dark solid orange */}
        <button
          onClick={handleSend}
          disabled={input.trim() === '' || isLoading}
          className="bg-orange-500 hover:bg-orange-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-5 py-3 rounded-2xl text-sm transition-all shadow-md shadow-orange-300"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>

      {/* Keyboard shortcut hint */}
      <p className="text-center text-xs text-slate-400 mt-2">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
