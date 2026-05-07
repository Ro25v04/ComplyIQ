"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_MESSAGES = [
  "Searching documents...",
  "Analysing...",
  "Compiling response...",
];

type Message = {
  role: "user" | "agent";
  content: string;
};

export default function AppPage() {
  const [documents, setDocuments] = useState<{ filename: string; chunks: number }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [querying, setQuerying] = useState(false);
  const [statusIndex, setStatusIndex] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const statusTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, querying]);

  useEffect(() => {
    if (querying) {
      setStatusIndex(0);
      statusTimer.current = setInterval(() => {
        setStatusIndex((i) => (i + 1) % STATUS_MESSAGES.length);
      }, 2500);
    } else {
      if (statusTimer.current) clearInterval(statusTimer.current);
    }
    return () => {
      if (statusTimer.current) clearInterval(statusTimer.current);
    };
  }, [querying]);

  async function fetchDocuments() {
    try {
      const res = await fetch(`${API_URL}/documents`);
      if (res.ok) setDocuments(await res.json());
    } catch {}
  }

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
      setUploadMsg(`✓ ${data.filename} — ${data.chunks_indexed} chunks indexed`);
      fetchDocuments();
    } catch (err: unknown) {
      setUploadMsg(`✗ ${err instanceof Error ? err.message : "Upload failed"}`);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleQuery(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || querying) return;

    const userMessage = question.trim();
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setQuerying(true);

    try {
      const history = messages.slice(-10);
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage, history }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");
      setMessages((prev) => [...prev, { role: "agent", content: data.answer }]);
    } catch (err: unknown) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: `Error: ${err instanceof Error ? err.message : "Something went wrong"}` },
      ]);
    } finally {
      setQuerying(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-white" style={{ colorScheme: "light" }}>
      {/* Navbar */}
      <nav className="bg-[#0F1C2E] text-white px-8 py-4 flex items-center justify-between shrink-0">
        <Link href="/" className="text-xl font-semibold tracking-tight hover:opacity-80 transition-opacity">
          ComplyIQ
        </Link>
        <span className="text-sm text-gray-300">Compliance Analyser</span>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Left panel — Documents */}
        <div className="w-72 shrink-0 flex flex-col border-r border-[#E5E7EB] bg-[#F8F9FA]">
          <div className="p-5 border-b border-[#E5E7EB]">
            <h2 className="font-semibold text-[#1A1A2E] mb-1">Documents</h2>
            <p className="text-xs text-[#6B7280]">Upload PDF or DOCX compliance documents</p>
          </div>

          {/* Upload area */}
          <div className="p-4">
            <div
              className="border-2 border-dashed border-[#E5E7EB] rounded-lg p-5 text-center cursor-pointer hover:border-[#0F1C2E] hover:bg-white transition-all duration-200"
              onClick={() => fileRef.current?.click()}
            >
              <div className="text-2xl mb-2">
                {uploading ? (
                  <span className="inline-block animate-spin">⏳</span>
                ) : "📄"}
              </div>
              <p className="text-sm text-[#6B7280] font-medium">
                {uploading ? "Uploading..." : "Click to upload"}
              </p>
              <p className="text-xs text-[#9CA3AF] mt-1">PDF or DOCX</p>
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
              <p className={`text-xs mt-2 ${uploadMsg.startsWith("✓") ? "text-green-600" : "text-red-500"}`}>
                {uploadMsg}
              </p>
            )}
          </div>

          {/* Document list */}
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-[#6B7280] uppercase tracking-wide">
                Indexed ({documents.length})
              </span>
              <button
                onClick={fetchDocuments}
                className="text-xs text-[#0F1C2E] hover:underline"
              >
                Refresh
              </button>
            </div>
            {documents.length === 0 ? (
              <p className="text-xs text-[#9CA3AF]">No documents uploaded yet</p>
            ) : (
              <ul className="space-y-2">
                {documents.map((doc) => (
                  <li key={doc.filename} className="bg-white border border-[#E5E7EB] rounded-lg p-3 flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-[#1A1A2E] truncate" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <p className="text-xs text-[#6B7280] mt-0.5">{doc.chunks} chunks indexed</p>
                    </div>
                    <button
                      onClick={async () => {
                        setDocuments((prev) => prev.filter((d) => d.filename !== doc.filename));
                        await fetch(`${API_URL}/documents/${encodeURIComponent(doc.filename)}`, { method: "DELETE" });
                      }}
                      className="text-[#9CA3AF] hover:text-red-500 transition-colors shrink-0 text-sm leading-none mt-0.5"
                      title="Delete document"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right panel — Chat */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages area */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
            {messages.length === 0 && !querying && (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="text-5xl mb-4">⚖️</div>
                <h3 className="font-semibold text-[#1A1A2E] mb-2">Ask a compliance question</h3>
                <p className="text-sm text-[#6B7280] max-w-sm">
                  Upload a document and ask anything about your compliance obligations under Australian law.
                </p>
                <div className="mt-6 grid grid-cols-1 gap-2 w-full max-w-md">
                  {[
                    "Is our privacy policy compliant with the Privacy Act 1988?",
                    "What are our data breach notification obligations?",
                    "Does this internship agreement comply with the Fair Work Act?",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setQuestion(suggestion)}
                      className="text-left text-xs text-[#6B7280] border border-[#E5E7EB] rounded-lg px-4 py-2.5 hover:border-[#0F1C2E] hover:text-[#1A1A2E] transition-all duration-150"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
              >
                {msg.role === "agent" && (
                  <div className="w-7 h-7 rounded-full bg-[#0F1C2E] text-white text-xs flex items-center justify-center mr-3 mt-1 shrink-0">
                    AI
                  </div>
                )}
                <div
                  className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-[#0F1C2E] text-white rounded-tr-sm whitespace-pre-wrap"
                      : "bg-[#F8F9FA] text-[#1A1A2E] border border-[#E5E7EB] rounded-tl-sm"
                  }`}
                >
                  {msg.role === "user" ? msg.content : (
                    <ReactMarkdown
                      components={{
                        h3: ({ children }) => <p className="font-semibold mt-2 mb-1">{children}</p>,
                        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                        ul: ({ children }) => <ul className="list-disc pl-4 space-y-1">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal pl-4 space-y-1">{children}</ol>,
                        li: ({ children }) => <li>{children}</li>,
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="w-7 h-7 rounded-full bg-gray-200 text-[#1A1A2E] text-xs flex items-center justify-center ml-3 mt-1 shrink-0">
                    You
                  </div>
                )}
              </div>
            ))}

            {/* Thinking indicator */}
            {querying && (
              <div className="flex justify-start animate-fade-in">
                <div className="w-7 h-7 rounded-full bg-[#0F1C2E] text-white text-xs flex items-center justify-center mr-3 mt-1 shrink-0">
                  AI
                </div>
                <div className="bg-[#F8F9FA] border border-[#E5E7EB] rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex items-center gap-2 text-sm text-[#6B7280]">
                    <span className="key={statusIndex}">{STATUS_MESSAGES[statusIndex]}</span>
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 bg-[#6B7280] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-1.5 h-1.5 bg-[#6B7280] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-1.5 h-1.5 bg-[#6B7280] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-[#E5E7EB] px-6 py-4 bg-white">
            <form onSubmit={handleQuery} className="flex gap-3 items-end">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleQuery(e as unknown as React.FormEvent);
                  }
                }}
                placeholder="Ask a compliance question... (Enter to send, Shift+Enter for new line)"
                rows={2}
                className="flex-1 border border-[#E5E7EB] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#0F1C2E] text-[#1A1A2E] resize-none bg-white placeholder-[#9CA3AF]"
                disabled={querying}
              />
              <button
                type="submit"
                disabled={querying || !question.trim()}
                className="bg-[#0F1C2E] text-white px-5 py-3 rounded-xl text-sm font-medium hover:bg-[#1B3A5C] transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              >
                {querying ? "..." : "Send"}
              </button>
            </form>
            <p className="text-xs text-[#9CA3AF] mt-2">
              ComplyIQ analyses Australian law in real time. Always verify with a qualified legal professional.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}