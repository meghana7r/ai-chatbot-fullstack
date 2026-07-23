'use client';

import { useState, useRef, useEffect } from 'react';
import { uploadDocument, fetchDocuments, deleteDocument } from '../utils/api';

// MIME type validation
const ALLOWED_MIME_TYPES: Record<string, string> = {
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'text/plain': '.txt',
};

const MAX_FILE_SIZE = 3 * 1024 * 1024; // 3MB

interface DocumentUploadProps {
  sessionId: string;
}

interface UploadedDoc {
  name: string;
  chunks?: number;
  is_current?: boolean;
}

export default function DocumentUpload({ sessionId }: DocumentUploadProps) {
  // Load from localStorage immediately as fallback
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDoc[]>(() => {
    try {
      const saved = localStorage.getItem(`docs_${sessionId}`);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [isUploading, setIsUploading] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<{ text: string; success: boolean } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch from API on load
  useEffect(() => {
    if (sessionId) {
      fetchDocuments(sessionId).then((result) => {
        if (result.documents.length > 0) {
          setUploadedDocs(result.documents);
          localStorage.setItem(`docs_${sessionId}`, JSON.stringify(result.documents));
        }
      });
    }
  }, [sessionId]);

  // Save to localStorage whenever docs change
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(`docs_${sessionId}`, JSON.stringify(uploadedDocs));
    }
  }, [uploadedDocs, sessionId]);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // MIME type validation
    if (!ALLOWED_MIME_TYPES[file.type]) {
      setStatusMessage({ text: '❌ Only PDF, DOCX, or TXT files are allowed.', success: false });
      return;
    }

    // File size validation
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      setStatusMessage({
        text: `❌ File too large! Max: 3MB. Your file: ${sizeMB}MB`,
        success: false,
      });
      return;
    }

    setIsUploading(true);
    setStatusMessage(null);

    const result = await uploadDocument(file, sessionId);

    if (result.success) {
      setStatusMessage({ text: '✅ ' + result.message, success: true });

      // Refresh document list from API
      const updated = await fetchDocuments(sessionId);
      if (updated.documents.length > 0) {
        setUploadedDocs(updated.documents);
      } else {
        // Fallback — add locally
        const newDoc: UploadedDoc = { name: file.name, is_current: true };
        setUploadedDocs((prev) => {
          const updated = prev.map(d => ({ ...d, is_current: false }));
          const merged = [...updated, newDoc];
          return merged.length > 5 ? merged.slice(-5) : merged;
        });
      }
    } else {
      setStatusMessage({ text: '❌ ' + result.message, success: false });
    }

    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Delete individual document
  const handleDelete = async (docName: string) => {
    setDeletingDoc(docName);
    setStatusMessage(null);

    const result = await deleteDocument(sessionId, docName);

    if (result.success) {
      // Remove from local list
      setUploadedDocs((prev) => prev.filter((d) => d.name !== docName));
      setStatusMessage({ text: '✅ File deleted successfully', success: true });
    } else {
      setStatusMessage({ text: '❌ ' + result.message, success: false });
    }

    setDeletingDoc(null);
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

      {/* Upload button */}
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        className="w-full py-2 rounded-xl border border-dashed border-rose-300 text-rose-400 text-xs font-medium hover:bg-rose-50 transition-all disabled:opacity-50"
      >
        {isUploading ? '⏳ Uploading...' : '+ Upload PDF / DOCX / TXT'}
      </button>

      {/* Uploaded documents list */}
      {uploadedDocs.length > 0 && (
        <div className="mt-2 flex flex-col gap-1">
          {uploadedDocs.map((doc, index) => (
            <div
              key={index}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs border ${
                doc.is_current
                  ? 'bg-rose-50 border-rose-200 text-slate-700'
                  : 'bg-slate-50 border-slate-100 text-slate-400'
              }`}
            >
              <span className="truncate flex-1">📎 {doc.name}</span>
              {doc.is_current && (
                <span className="text-green-500 text-[10px] flex-shrink-0">✓</span>
              )}
              {/* Delete button */}
              <button
                onClick={() => handleDelete(doc.name)}
                disabled={deletingDoc === doc.name}
                className="text-slate-300 hover:text-rose-400 text-xs flex-shrink-0 transition-colors disabled:opacity-50"
                title="Delete file"
              >
                {deletingDoc === doc.name ? '...' : '🗑️'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Status message */}
      {statusMessage && (
        <p className={`text-[11px] mt-2 leading-relaxed ${statusMessage.success ? 'text-green-500' : 'text-red-400'}`}>
          {statusMessage.text}
        </p>
      )}

      <p className="text-slate-300 text-[10px] mt-2">
        Max 3MB · PDF, DOCX, TXT · Max 5 files
      </p>
    </div>
  );
}
