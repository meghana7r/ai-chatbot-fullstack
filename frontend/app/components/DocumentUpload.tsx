'use client';

// DocumentUpload.tsx — Week 6: RAG document upload section for sidebar
// Built by Meghana Ravi

import { useState, useRef } from 'react';
import { uploadDocument } from '../utils/api';

export default function DocumentUpload() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ text: string; success: boolean } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedExtensions = ['.pdf', '.docx', '.txt'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedExtensions.includes(fileExt)) {
      setStatusMessage({ text: 'Only PDF, DOCX, or TXT files are allowed.', success: false });
      return;
    }

    setIsUploading(true);
    setStatusMessage(null);

    const result = await uploadDocument(file);

    if (result.success) {
      setFileName(file.name);
      setStatusMessage({ text: result.message, success: true });
    } else {
      setStatusMessage({ text: result.message, success: false });
    }

    setIsUploading(false);
  };

  const handleDelete = () => {
    setFileName(null);
    setStatusMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="px-3 py-3 border-t border-orange-100">
      <p className="text-slate-700 font-semibold text-xs mb-2 flex items-center gap-1.5">
        📄 Document Upload
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileSelect}
        className="hidden"
      />

      {!fileName && (
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="w-full py-2 rounded-xl border border-dashed border-rose-300 text-rose-400 text-xs font-medium hover:bg-rose-50 transition-all disabled:opacity-50"
        >
          {isUploading ? 'Uploading...' : '+ Upload PDF / DOCX / TXT'}
        </button>
      )}

      {fileName && (
        <div className="flex items-center justify-between gap-2 px-3 py-2 rounded-xl bg-rose-50 border border-rose-100">
          <span className="text-slate-600 text-xs truncate flex-1">📎 {fileName}</span>
          <button
            onClick={handleDelete}
            className="text-slate-300 hover:text-rose-400 text-xs flex-shrink-0"
          >
            ✕
          </button>
        </div>
      )}

      {statusMessage && (
        <p className={`text-[11px] mt-2 ${statusMessage.success ? 'text-green-500' : 'text-red-400'}`}>
          {statusMessage.text}
        </p>
      )}
    </div>
  );
}
