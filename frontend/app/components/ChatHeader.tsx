// ChatHeader.tsx — Top bar of the chat window
// Built by Meghana Ravi
// Shows MegaBot name, online status, message counter, Home link and Clear Chat button
// Week 3: Added hamburger menu button for mobile sidebar

import Link from 'next/link';

interface ChatHeaderProps {
  messageCount: number;
  onClear: () => void;
  onMenuClick: () => void; // opens sidebar on mobile
}

export default function ChatHeader({ messageCount, onClear, onMenuClick }: ChatHeaderProps) {
  return (
    <div className="border-b border-orange-200 px-4 py-4 bg-white flex items-center justify-between shadow-sm">

      {/* Left side — hamburger + MegaBot avatar + name + online status */}
      <div className="flex items-center gap-3">

        {/* Hamburger menu — only visible on mobile to open sidebar */}
        <button
          onClick={onMenuClick}
          className="md:hidden mr-1 text-slate-400 hover:text-rose-500 text-xl"
        >
          ☰
        </button>

        {/* Avatar — rose to orange gradient */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-rose-500 to-orange-400 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-orange-200">
          M
        </div>
        <div>
          <h1 className="text-slate-800 font-semibold text-sm">MegaBot</h1>
          <p className="text-green-500 text-xs">● Online</p>
        </div>
      </div>

      {/* Right side — message counter + clear button + home link */}
      <div className="flex items-center gap-3">

        {/* Message counter — Meghana's extra feature */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-50 border border-orange-200">
          <span className="text-orange-400 text-xs">💬</span>
          <span className="text-orange-600 text-xs font-medium">{messageCount} messages</span>
        </div>

        {/* Clear chat button */}
        <button
          onClick={onClear}
          className="px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-400 text-xs font-medium hover:bg-rose-100 hover:text-rose-600 transition-all"
        >
          🗑️ Clear
        </button>

        {/* Home link */}
        <Link
          href="/"
          className="text-slate-400 hover:text-orange-500 text-xs transition-colors font-medium"
        >
          ← Home
        </Link>
      </div>
    </div>
  );
}
