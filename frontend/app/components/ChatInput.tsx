import { useState } from 'react';

type ChatInputProps = {
  onSend: (message: string) => void;
  isLoading: boolean;
};

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() === '' || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-slate-700 px-4 py-4 bg-[#0f0f1a]">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
          rows={1}
          className="flex-1 resize-none bg-slate-800 text-slate-200 placeholder-slate-500 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-500 border border-slate-700"
        />
        <button
          onClick={handleSend}
          disabled={input.trim() === '' || isLoading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-2xl text-sm font-semibold transition-all"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
      <p className="text-center text-xs text-slate-600 mt-2">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
