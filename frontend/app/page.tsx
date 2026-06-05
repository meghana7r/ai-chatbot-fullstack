// page.tsx — MegaBot Homepage
// Built by Meghana Ravi
// Landing page with Learn More modal popup

'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Home() {
  // Controls whether the Learn More modal is open or closed
  const [showModal, setShowModal] = useState(false);

  return (
    <main className="min-h-screen bg-[#fff8f5] flex flex-col items-center justify-center px-4 text-center relative overflow-hidden">

      {/* Background decorative blobs */}
      <div className="absolute top-[-80px] left-[-80px] w-[400px] h-[400px] rounded-full bg-rose-300/30 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-60px] right-[-60px] w-[350px] h-[350px] rounded-full bg-orange-300/30 blur-[100px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/4 w-[200px] h-[200px] rounded-full bg-rose-200/20 blur-[80px] pointer-events-none" />

      {/* Badge pill */}
      <div className="mb-6 px-4 py-1.5 rounded-full border border-rose-400/40 bg-rose-100 text-rose-600 text-xs font-medium tracking-widest uppercase">
        ✦ MegaBot — Your Smart Assistant
      </div>

      {/* Main heading */}
      <h1 className="text-5xl sm:text-6xl font-bold text-slate-900 mb-4 leading-tight tracking-tight">
        Chat with{' '}
        <span className="bg-gradient-to-r from-rose-500 to-orange-500 bg-clip-text text-transparent">
          MegaBot
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-slate-500 text-lg max-w-md mb-10 leading-relaxed">
        Ask anything, get instant answers. Your intelligent assistant is ready to help you 24/7.
      </p>

      {/* Feature pills */}
      <div className="flex flex-wrap justify-center gap-2 mb-10">
        {['⚡ Instant Replies', '🧠 Smart Answers', '💬 Message Counter'].map((feature) => (
          <span
            key={feature}
            className="px-3 py-1 rounded-full bg-white/80 border border-rose-200/60 text-slate-600 text-xs shadow-sm"
          >
            {feature}
          </span>
        ))}
      </div>

      {/* CTA Buttons */}
      <div className="flex gap-4 flex-wrap justify-center">
        <Link href="/chat">
          <button className="px-7 py-3 rounded-full bg-gradient-to-r from-rose-500 to-orange-500 text-white font-semibold text-sm hover:opacity-90 hover:scale-105 transition-all duration-200 shadow-lg shadow-rose-400/30">
            Start Chatting →
          </button>
        </Link>

        {/* Learn More — opens the modal */}
        <button
          onClick={() => setShowModal(true)}
          className="px-7 py-3 rounded-full border border-slate-400 text-slate-600 font-semibold text-sm hover:border-rose-400 hover:text-rose-500 transition-all duration-200"
        >
          Learn More
        </button>
      </div>

      {/* Stats row */}
      <div className="mt-14 flex gap-8 flex-wrap justify-center">
        {[
          { value: '24/7', label: 'Always Online' },
          { value: '< 1s', label: 'Response Time' },
          { value: '∞', label: 'Questions Asked' },
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <p className="text-2xl font-bold bg-gradient-to-r from-rose-500 to-orange-500 bg-clip-text text-transparent">
              {stat.value}
            </p>
            <p className="text-slate-400 text-xs mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Footer */}
      <p className="mt-12 text-slate-400 text-xs">
        Built by{' '}
        <span className="text-rose-500 font-medium">Meghana Ravi</span>
        {' '}· Next.js · TypeScript · Tailwind CSS
      </p>

      {/* ── Learn More Modal ── */}
      {showModal && (
        // Dark overlay — clicking it closes the modal
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4"
          onClick={() => setShowModal(false)}
        >
          {/* Modal box — stop click from closing when clicking inside */}
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-rose-500 text-xl font-bold transition-colors"
            >
              ✕
            </button>

            {/* Modal header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-rose-500 to-orange-400 flex items-center justify-center text-white font-bold text-sm">
                M
              </div>
              <div>
                <div>
  <h2 className="text-slate-900 font-bold text-lg">About MegaBot</h2>
  <p className="text-slate-400 text-xs">Frontend: Meghana Ravi · Backend: Amrutha Varshini</p>
</div>
              
              </div>
            </div>

            {/* Feature list */}
            <div className="flex flex-col gap-4">
              {[
                {
                  icon: '🤖',
                  title: 'Groq Llama 3 AI',
                  desc: 'Powered by the latest Llama 3 model via Groq — fast, smart, and free.',
                },
                {
                  icon: '🧠',
                  title: 'Conversation Memory',
                  desc: 'MegaBot remembers your full conversation and keeps context across messages.',
                },
                {
                  icon: '⚡',
                  title: 'Instant Replies',
                  desc: 'FastAPI Python backend delivers responses in under a second.',
                },
                {
                  icon: '💬',
                  title: 'Message Counter',
                  desc: 'Live count of messages sent — visible in the chat header.',
                },
                {
                  icon: '🗑️',
                  title: 'Clear Chat',
                  desc: 'Reset the conversation anytime with the clear button.',
                },
                {
                  icon: '🎨',
                  title: 'Custom Design',
                  desc: 'Rose & orange theme, personalised UI — designed by Meghana Ravi.',
                },
              ].map((item) => (
                <div key={item.title} className="flex items-start gap-3">
                  <span className="text-xl mt-0.5">{item.icon}</span>
                  <div>
                    <p className="text-slate-800 font-semibold text-sm">{item.title}</p>
                    <p className="text-slate-400 text-xs leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
{/* Built by section */}
<div className="mt-6 p-4 bg-rose-50 rounded-xl border border-rose-100">
  <p className="text-slate-500 text-xs font-semibold mb-2">👩‍💻 Built by</p>
  <div className="flex justify-between">
    <div>
      <p className="text-slate-700 text-sm font-medium">Meghana Ravi</p>
      <p className="text-rose-400 text-xs">Frontend Developer</p>
    </div>
    <div className="text-right">
      <p className="text-slate-700 text-sm font-medium">Amrutha Varshini</p>
      <p className="text-rose-400 text-xs">Backend Developer</p>
    </div>
  </div>
</div>
            {/* Modal footer button */}
            <Link href="/chat">
              <button className="mt-6 w-full py-3 rounded-full bg-gradient-to-r from-rose-500 to-orange-500 text-white font-semibold text-sm hover:opacity-90 transition-all">
                Start Chatting →
              </button>
            </Link>
          </div>
        </div>
      )}
    </main>
  );
}
