import Link from 'next/link';

export default function ChatHeader() {
  return (
    <div className="border-b border-slate-700 px-6 py-4 bg-[#0f0f1a] flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
          AI
        </div>
        <div>
          <h1 className="text-white font-semibold text-sm">AI Chatbot</h1>
          <p className="text-green-400 text-xs">● Online</p>
        </div>
      </div>
      <Link href="/" className="text-slate-400 hover:text-white text-xs transition-colors">
        ← Home
      </Link>
    </div>
  );
}
