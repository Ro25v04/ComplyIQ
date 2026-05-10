"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_MESSAGES = ["Searching documents...", "Analysing legislation...", "Compiling response..."];

type Message = { role: "user" | "agent"; content: string };

export default function AppPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<{ filename: string; chunks: number }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [querying, setQuerying] = useState(false);
  const [statusIndex, setStatusIndex] = useState(0);
  const [generatingReport, setGeneratingReport] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const statusTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => { fetchDocuments(); }, []);

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
    return () => { if (statusTimer.current) clearInterval(statusTimer.current); };
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

  async function handleQuery(e: { preventDefault(): void }) {
    e.preventDefault();
    if (!question.trim() || querying) return;
    const userMessage = question.trim();
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setQuerying(true);
    try {
      const history = messages.slice(-10);
      const res = await fetch(`${API_URL}/query/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage, history }),
      });
      if (!res.ok) throw new Error("Query failed");
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let isFirstChunk = true;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullContent += decoder.decode(value);
        if (isFirstChunk) {
          setQuerying(false);
          setMessages((prev) => [...prev, { role: "agent", content: fullContent }]);
          isFirstChunk = false;
        } else {
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: "agent", content: fullContent };
            return updated;
          });
        }
      }
    } catch (err: unknown) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: `Error: ${err instanceof Error ? err.message : "Something went wrong"}` },
      ]);
    } finally {
      setQuerying(false);
    }
  }

  async function handleGenerateReport() {
    if (messages.length < 2) return;
    setGeneratingReport(true);
    try {
      const res = await fetch(`${API_URL}/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: messages }),
      });
      if (!res.ok) throw new Error("Report generation failed");
      const data = await res.json();
      localStorage.setItem("complyau_report", JSON.stringify(data));
      router.push("/report");
    } catch (err) {
      console.error(err);
      alert("Failed to generate report. Please try again.");
    } finally {
      setGeneratingReport(false);
    }
  }

  const agentMessageCount = messages.filter((m) => m.role === "agent").length;

  return (
    <div className="min-h-screen flex bg-[#F8F9FF]" style={{ colorScheme: "light" }}>
      {/* Sidebar */}
      <aside className="w-72 shrink-0 flex flex-col bg-[#0F1C2E] h-screen sticky top-0">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-white/10">
          <Link href="/" className="text-white font-bold text-lg hover:opacity-80 transition-opacity">
            ComplyAU
          </Link>
          <p className="text-[#78849B] text-xs mt-0.5">Compliance Analyser</p>
        </div>

        {/* Upload area */}
        <div className="p-4 border-b border-white/10">
          <div
            className="border-2 border-dashed border-white/20 rounded-lg p-4 text-center cursor-pointer hover:border-white/40 hover:bg-white/5 transition-all duration-200"
            onClick={() => fileRef.current?.click()}
          >
            <div className="text-2xl mb-1">{uploading ? <span className="inline-block animate-spin">⏳</span> : "📄"}</div>
            <p className="text-sm text-[#BAC7DF] font-medium">{uploading ? "Uploading..." : "Upload Document"}</p>
            <p className="text-xs text-[#78849B] mt-0.5">PDF or DOCX</p>
            <input ref={fileRef} type="file" accept=".pdf,.docx,.doc" className="hidden" onChange={handleUpload} disabled={uploading} />
          </div>
          {uploadMsg && (
            <p className={`text-xs mt-2 ${uploadMsg.startsWith("✓") ? "text-green-400" : "text-red-400"}`}>
              {uploadMsg}
            </p>
          )}
        </div>

        {/* Document list */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-[#78849B] uppercase tracking-wide">
              Documents ({documents.length})
            </span>
            <button onClick={fetchDocuments} className="text-xs text-[#BAC7DF] hover:text-white transition-colors">
              Refresh
            </button>
          </div>
          {documents.length === 0 ? (
            <p className="text-xs text-[#78849B]">No documents uploaded yet</p>
          ) : (
            <ul className="space-y-2">
              {documents.map((doc) => (
                <li key={doc.filename} className="bg-white/5 border border-white/10 rounded-lg p-3 flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-[#D6E3FC] truncate" title={doc.filename}>
                      {doc.filename}
                    </p>
                    <p className="text-xs text-[#78849B] mt-0.5">{doc.chunks} chunks indexed</p>
                  </div>
                  <button
                    onClick={async () => {
                      setDocuments((prev) => prev.filter((d) => d.filename !== doc.filename));
                      await fetch(`${API_URL}/documents/${encodeURIComponent(doc.filename)}`, { method: "DELETE" });
                    }}
                    className="text-[#78849B] hover:text-red-400 transition-colors shrink-0 text-sm"
                    title="Delete document"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Generate Report button */}
        {agentMessageCount >= 1 && (
          <div className="p-4 border-t border-white/10">
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="w-full bg-[#D6E3FC] text-[#0F1C2E] font-semibold text-sm py-2.5 rounded hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingReport ? "Generating..." : "Generate Report →"}
            </button>
          </div>
        )}
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <header className="bg-[#F8F9FF] border-b border-[#C5C6CD] px-6 py-4 flex items-center justify-between shrink-0">
          <h2 className="font-semibold text-[#0B1C30]">AI Analysis</h2>
          <span className="text-xs text-[#44474C]">Powered by GPT-4o mini · Australian law</span>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.length === 0 && !querying && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="text-5xl mb-4">⚖️</div>
              <h3 className="font-semibold text-[#0B1C30] mb-2">Ask a compliance question</h3>
              <p className="text-sm text-[#44474C] max-w-sm">
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
                    className="text-left text-xs text-[#44474C] border border-[#C5C6CD] rounded-lg px-4 py-2.5 hover:border-[#0F1C2E] hover:text-[#0B1C30] transition-all duration-150 bg-white"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}>
              {msg.role === "agent" && (
                <div className="w-7 h-7 rounded bg-[#0F1C2E] text-white text-xs flex items-center justify-center mr-3 mt-1 shrink-0 font-semibold">
                  AI
                </div>
              )}
              <div
                className={`max-w-2xl rounded-lg px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-[#0F1C2E] text-white rounded-tr-sm border-2 border-[#0F1C2E]"
                    : "bg-[#DCE9FF] text-[#0B1C30] border border-[#C5C6CD] rounded-tl-sm"
                }`}
              >
                {msg.role === "user" ? (
                  <span className="whitespace-pre-wrap">{msg.content}</span>
                ) : (
                  <ReactMarkdown
                    components={{
                      h3: ({ children }) => <p className="font-semibold mt-2 mb-1">{children}</p>,
                      h4: ({ children }) => <p className="font-semibold text-xs uppercase tracking-wide mt-2 mb-1 text-[#44474C]">{children}</p>,
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
                <div className="w-7 h-7 rounded bg-[#D6E3FC] text-[#0F1C2E] text-xs flex items-center justify-center ml-3 mt-1 shrink-0 font-semibold">
                  You
                </div>
              )}
            </div>
          ))}

          {querying && (
            <div className="flex justify-start animate-fade-in">
              <div className="w-7 h-7 rounded bg-[#0F1C2E] text-white text-xs flex items-center justify-center mr-3 mt-1 shrink-0 font-semibold">
                AI
              </div>
              <div className="bg-[#DCE9FF] border border-[#C5C6CD] rounded-lg rounded-tl-sm px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-[#44474C]">
                  <span>{STATUS_MESSAGES[statusIndex]}</span>
                  <span className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-[#44474C] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 bg-[#44474C] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 bg-[#44474C] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-[#C5C6CD] px-6 py-4 bg-white shrink-0">
          <form onSubmit={handleQuery} className="flex gap-3 items-end">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleQuery(e);
                }
              }}
              placeholder="Ask a compliance question... (Enter to send, Shift+Enter for new line)"
              rows={2}
              className="flex-1 border border-[#C5C6CD] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0F1C2E] text-[#0B1C30] resize-none bg-white placeholder-[#44474C]"
              disabled={querying}
            />
            <button
              type="submit"
              disabled={querying || !question.trim()}
              className="bg-[#0F1C2E] text-white px-5 py-3 rounded-lg text-sm font-semibold hover:bg-[#1B3A5C] transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            >
              {querying ? "..." : "Send"}
            </button>
          </form>
          <p className="text-xs text-[#44474C] mt-2">
            ComplyAU analyses Australian law in real time. Always verify with a qualified legal professional.
          </p>
        </div>
      </div>
    </div>
  );
}