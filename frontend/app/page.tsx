import Link from 'next/link';
import Button from './components/Button';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0f0f1a] flex flex-col items-center justify-center px-4 text-center">
      <div className="mb-6 px-4 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-medium tracking-wide">
        AI Powered Chatbot
      </div>
      <h1 className="text-5xl font-bold text-white mb-4 leading-tight">
        Chat with <span className="text-indigo-400">AI</span>
      </h1>
      <p className="text-slate-400 text-lg max-w-md mb-10">
        Ask anything, get instant answers. Your intelligent assistant is ready to help you 24/7.
      </p>
      <div className="flex gap-4">
        <Link href="/chat">
          <Button label="Start Chatting →" variant="primary" />
        </Link>
        <Button label="Learn More" variant="secondary" />
      </div>
      <p className="mt-12 text-slate-600 text-xs">
        Built with Next.js · TypeScript · Tailwind CSS
      </p>
    </main>
  );
}
