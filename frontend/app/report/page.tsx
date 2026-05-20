"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

type Gap = {
  regulation: string;
  description: string;
  severity: "critical" | "major" | "minor";
};

type Recommendation = {
  title: string;
  description: string;
};

type ReportData = {
  document_name: string;
  score: number;
  risk_level: "Low" | "Medium" | "High";
  gaps: Gap[];
  recommendations: Recommendation[];
};

const SEVERITY_STYLES: Record<string, { badge: string; label: string }> = {
  critical: { badge: "bg-[#FFDAD6] text-[#93000A]", label: "Critical" },
  major:    { badge: "bg-[#FFF3CD] text-[#7B4F00]", label: "Major" },
  minor:    { badge: "bg-[#DCE9FF] text-[#0F1C2E]", label: "Minor" },
};

const RISK_STYLES: Record<string, string> = {
  Low:    "text-green-700 bg-green-50 border-green-200",
  Medium: "text-yellow-700 bg-yellow-50 border-yellow-200",
  High:   "text-[#93000A] bg-[#FFDAD6] border-[#FFDAD6]",
};

function ScoreGauge({ score }: { score: number }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative w-44 h-44 flex items-center justify-center">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
        <circle
          cx="80" cy="80" r={radius}
          fill="transparent"
          stroke="#DCE9FF"
          strokeWidth="12"
        />
        <circle
          cx="80" cy="80" r={radius}
          fill="transparent"
          stroke="#0F1C2E"
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute text-3xl font-bold text-[#0B1C30]">
        {score}
        <span className="text-lg font-normal text-[#44474C]">/100</span>
      </span>
    </div>
  );
}

export default function ReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<ReportData | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("complyau_report");
    if (!raw) {
      router.replace("/app");
      return;
    }
    setReport(JSON.parse(raw));
  }, [router]);

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8F9FF]">
        <p className="text-[#44474C] text-sm">Loading report...</p>
      </div>
    );
  }

  const criticalCount = report.gaps.filter((g) => g.severity === "critical").length;
  const majorCount = report.gaps.filter((g) => g.severity === "major").length;

  return (
    <div className="min-h-screen bg-[#F8F9FF]">
      {/* Navbar */}
      <header className="bg-[#F8F9FF] border-b border-[#C5C6CD] sticky top-0 z-50 no-print">
        <div className="max-w-5xl mx-auto px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/app" className="text-[#44474C] hover:text-[#0B1C30] transition-colors text-sm flex items-center gap-1">
              ← Back
            </Link>
            <span className="text-[#C5C6CD]">|</span>
            <span className="font-bold text-[#0F1C2E]">ComplyAU</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-[#44474C]">
            <Link href="/" className="hover:text-[#0B1C30] transition-colors">Home</Link>
            <span className="text-[#0B1C30] border-b-2 border-[#0B1C30] pb-0.5">Compliance Report</span>
          </nav>
          <div className="flex gap-3">
            <button
              onClick={() => window.print()}
              className="border border-[#C5C6CD] text-[#0B1C30] text-sm font-semibold px-4 py-2 rounded hover:bg-[#EFF4FF] transition-colors flex items-center gap-2"
            >
              ↓ PDF
            </button>
            <Link
              href="/app"
              className="bg-[#0F1C2E] text-white text-sm font-semibold px-4 py-2 rounded hover:bg-[#1B3A5C] transition-colors"
            >
              New Analysis
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-8 py-10 space-y-8">
        {/* Report header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-widest text-[#44474C]">
              Compliance Analysis Report
            </span>
            <h1 className="text-3xl font-bold text-[#0B1C30] mt-1">Regulatory Compliance Report</h1>
            <p className="text-sm text-[#44474C] mt-1">
              Document: <span className="font-semibold text-[#0B1C30]">{report.document_name}</span>
            </p>
          </div>
          <div className={`px-4 py-2 rounded border text-sm font-semibold ${RISK_STYLES[report.risk_level]}`}>
            {report.risk_level} Risk
          </div>
        </div>

        {/* Score + summary grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Score card */}
          <div className="md:col-span-4 bg-white border border-[#C5C6CD] rounded-xl p-6 flex flex-col items-center text-center">
            <span className="text-xs font-semibold uppercase tracking-widest text-[#44474C] mb-4">
              Overall Compliance Score
            </span>
            <ScoreGauge score={report.score} />
            <div className={`mt-4 px-3 py-1.5 rounded border text-xs font-semibold ${RISK_STYLES[report.risk_level]}`}>
              {report.risk_level} Risk
            </div>
            <div className="mt-4 w-full grid grid-cols-3 gap-2 text-center">
              <div className="bg-[#FFDAD6] rounded p-2">
                <span className="block text-lg font-bold text-[#93000A]">{criticalCount}</span>
                <span className="text-[10px] text-[#93000A] font-semibold">Critical</span>
              </div>
              <div className="bg-[#FFF3CD] rounded p-2">
                <span className="block text-lg font-bold text-[#7B4F00]">{majorCount}</span>
                <span className="text-[10px] text-[#7B4F00] font-semibold">Major</span>
              </div>
              <div className="bg-[#DCE9FF] rounded p-2">
                <span className="block text-lg font-bold text-[#0F1C2E]">
                  {report.gaps.length - criticalCount - majorCount}
                </span>
                <span className="text-[10px] text-[#0F1C2E] font-semibold">Minor</span>
              </div>
            </div>
          </div>

          {/* Risk distribution */}
          <div className="md:col-span-8 bg-white border border-[#C5C6CD] rounded-xl p-6">
            <h3 className="font-semibold text-[#0B1C30] mb-5">Risk Distribution</h3>
            <div className="space-y-5">
              {[
                { label: "Critical Gaps", count: criticalCount, total: report.gaps.length || 1, color: "bg-[#BA1A1A]" },
                { label: "Major Gaps",    count: majorCount,    total: report.gaps.length || 1, color: "bg-[#E08C00]" },
                { label: "Minor Gaps",    count: report.gaps.length - criticalCount - majorCount, total: report.gaps.length || 1, color: "bg-[#0F1C2E]" },
              ].map((row) => (
                <div key={row.label}>
                  <div className="flex justify-between text-sm font-semibold mb-1.5">
                    <span className="text-[#0B1C30]">{row.label}</span>
                    <span className="text-[#44474C]">{row.count} / {report.gaps.length}</span>
                  </div>
                  <div className="w-full bg-[#DCE9FF] h-2 rounded-full">
                    <div
                      className={`${row.color} h-2 rounded-full transition-all`}
                      style={{ width: `${(row.count / row.total) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 p-3 bg-[#EFF4FF] border border-[#C5C6CD] rounded text-sm text-[#44474C]">
              <strong className="text-[#0B1C30]">Note:</strong> Scoring deducts 20 pts per critical gap, 10 pts per major, and 5 pts per minor gap from a base of 100.
            </div>
          </div>
        </div>

        {/* Gaps table */}
        <div className="bg-white border border-[#C5C6CD] rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-[#C5C6CD] bg-[#EFF4FF] flex justify-between items-center">
            <h3 className="font-semibold text-[#0B1C30]">Identified Regulatory Gaps</h3>
            <span className="text-sm text-[#44474C]">{report.gaps.length} gap{report.gaps.length !== 1 ? "s" : ""} found</span>
          </div>
          {report.gaps.length === 0 ? (
            <div className="px-6 py-8 text-center text-[#44474C] text-sm">
              No compliance gaps identified in this conversation.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-[#DCE9FF] text-xs font-semibold uppercase tracking-wide text-[#0B1C30]">
                  <tr>
                    <th className="px-6 py-3">Regulation</th>
                    <th className="px-6 py-3">Gap Description</th>
                    <th className="px-6 py-3">Severity</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-[#EFF4FF]">
                  {report.gaps.map((gap, i) => (
                    <tr key={i} className={i % 2 === 1 ? "bg-[#F8F9FF]" : "bg-white"}>
                      <td className="px-6 py-4 font-semibold text-[#0B1C30] whitespace-nowrap">{gap.regulation}</td>
                      <td className="px-6 py-4 text-[#44474C]">{gap.description}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 rounded text-xs font-semibold ${SEVERITY_STYLES[gap.severity]?.badge ?? "bg-gray-100 text-gray-600"}`}>
                          {SEVERITY_STYLES[gap.severity]?.label ?? gap.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recommendations */}
        {report.recommendations.length > 0 && (
          <div>
            <h3 className="font-semibold text-[#0B1C30] mb-4">AI Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {report.recommendations.map((rec, i) => (
                <div
                  key={i}
                  className={`p-5 rounded-xl flex flex-col gap-2 ${
                    i === 0 ? "bg-[#0F1C2E] text-white" : "bg-white border border-[#C5C6CD]"
                  }`}
                >
                  <h4 className={`font-semibold text-base ${i === 0 ? "text-[#D6E3FC]" : "text-[#0B1C30]"}`}>
                    {rec.title}
                  </h4>
                  <p className={`text-sm leading-relaxed ${i === 0 ? "text-[#BAC7DF]" : "text-[#44474C]"}`}>
                    {rec.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer note */}
        <div className="border-t border-[#C5C6CD] pt-6 text-xs text-[#44474C] text-center no-print">
          ComplyAU analyses Australian law in real time. This report is AI-generated and should be verified with a qualified legal professional.
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-[#0F1C2E] mt-10 no-print">
        <div className="max-w-5xl mx-auto px-8 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <span className="font-bold text-white">ComplyAU</span>
          <p className="text-sm text-[#78849B]">Built for Australian businesses.</p>
          <div className="flex gap-6">
            {["Privacy Policy", "Terms of Service", "Contact"].map((link) => (
              <a key={link} href="#" className="text-sm text-[#78849B] hover:text-white transition-colors">{link}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}