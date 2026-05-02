"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AppPage() {
  const [documents, setDocuments] = useState<{ filename: string; chunks: number }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [querying, setQuerying] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { fetchDocuments(); }, []);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMsg("");

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setUploadMsg(`✓ ${data.filename} uploaded — ${data.chunks_indexed} chunks indexed`);
      fetchDocuments();
    } catch (err: any) {
      setUploadMsg(`✗ ${err.message}`);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function fetchDocuments() {
    try {
      const res = await fetch(`${API_URL}/documents`);
      if (res.ok) setDocuments(await res.json());
    } catch {
      // silently fail — backend may not be running
    }
  }

  async function handleQuery(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;

    setQuerying(true);
    setAnswer("");

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");
      setAnswer(data.answer);
    } catch (err: any) {
      setAnswer(`Error: ${err.message}`);
    } finally {
      setQuerying(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-[#0F1C2E] text-white px-8 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-semibold tracking-tight hover:opacity-80 transition-opacity">
          ComplyIQ
        </Link>
        <span className="text-sm text-gray-300">Compliance Analyser</span>
      </nav>

      <div className="flex flex-1 divide-x divide-[#E5E7EB]">
        {/* Left panel — Upload */}
        <div className="w-80 shrink-0 p-6 flex flex-col gap-6 bg-[#F8F9FA]">
          <div>
            <h2 className="font-semibold text-[#1A1A2E] mb-1">Documents</h2>
            <p className="text-xs text-[#6B7280]">Upload PDF or DOCX compliance documents</p>
          </div>

          {/* Upload area */}
          <div
            className="border-2 border-dashed border-[#E5E7EB] rounded-lg p-6 text-center cursor-pointer hover:border-[#0F1C2E] transition-colors"
            onClick={() => fileRef.current?.click()}
          >
            <div className="text-2xl mb-2">📄</div>
            <p className="text-sm text-[#6B7280]">
              {uploading ? "Uploading..." : "Click to upload"}
            </p>
            <p className="text-xs text-[#9CA3AF] mt-1">PDF, DOCX</p>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx,.doc"
              className="hidden"
              onChange={handleUpload}
              disabled={uploading}
            />
          </div>

          {uploadMsg && (
            <p className={`text-xs ${uploadMsg.startsWith("✓") ? "text-green-600" : "text-red-500"}`}>
              {uploadMsg}
            </p>
          )}

          {/* Document list */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-medium text-[#6B7280] uppercase tracking-wide">Indexed Documents</h3>
              <button onClick={fetchDocuments} className="text-xs text-[#0F1C2E] hover:underline">Refresh</button>
            </div>
            {documents.length === 0 ? (
              <p className="text-xs text-[#9CA3AF]">No documents uploaded yet</p>
            ) : (
              <ul className="space-y-2">
                {documents.map((doc) => (
                  <li key={doc.filename} className="bg-white border border-[#E5E7EB] rounded p-3">
                    <p className="text-xs font-medium text-[#1A1A2E] truncate">{doc.filename}</p>
                    <p className="text-xs text-[#6B7280]">{doc.chunks} chunks</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right panel — Chat */}
        <div className="flex-1 flex flex-col p-8">
          <div className="max-w-2xl mx-auto w-full flex flex-col flex-1">
            <div className="mb-8">
              <h2 className="font-semibold text-[#1A1A2E] mb-1">Ask a compliance question</h2>
              <p className="text-sm text-[#6B7280]">
                The AI agent will search your documents and live Australian legislation to analyse your compliance position.
              </p>
            </div>

            <form onSubmit={handleQuery} className="flex gap-3 mb-8">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Are we compliant with the Privacy Act data retention requirements?"
                className="flex-1 border border-[#E5E7EB] rounded px-4 py-2 text-sm focus:outline-none focus:border-[#0F1C2E] text-[#1A1A2E]"
                disabled={querying}
              />
              <button
                type="submit"
                disabled={querying || !question.trim()}
                className="bg-[#0F1C2E] text-white px-6 py-2 rounded text-sm font-medium hover:bg-[#1B3A5C] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {querying ? "Analysing..." : "Analyse"}
              </button>
            </form>

            {querying && (
              <div className="flex items-center gap-2 text-sm text-[#6B7280]">
                <div className="w-4 h-4 border-2 border-[#0F1C2E] border-t-transparent rounded-full animate-spin" />
                Agent is running — searching documents and legislation...
              </div>
            )}

            {answer && (
              <div className="border border-[#E5E7EB] rounded-lg p-6 bg-white">
                <h3 className="text-xs font-medium text-[#6B7280] uppercase tracking-wide mb-4">Analysis Result</h3>
                <div className="text-sm text-[#1A1A2E] leading-relaxed whitespace-pre-wrap">{answer}</div>
              </div>
            )}

            {!answer && !querying && (
              <div className="flex-1 flex items-center justify-center text-center">
                <div>
                  <div className="text-4xl mb-4">⚖️</div>
                  <p className="text-sm text-[#6B7280]">Upload a document and ask a compliance question to get started</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}