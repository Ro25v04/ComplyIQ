import Link from "next/link";

const FRAMEWORKS = [
  { code: "Privacy Act", sub: "1988" },
  { code: "Fair Work Act", sub: "2009" },
  { code: "Corporations Act", sub: "2001" },
  { code: "WHS Act", sub: "2011" },
  { code: "Consumer Law", sub: "ACL" },
  { code: "Spam Act", sub: "2003" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#F8F9FF]">
      {/* Navbar */}
      <header className="bg-[#F8F9FF] border-b border-[#C5C6CD] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-[#0F1C2E]">ComplyAU</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-semibold text-[#44474C] hover:text-[#0F1C2E] transition-colors tracking-wide">
              Features
            </a>
            <a href="#frameworks" className="text-sm font-semibold text-[#44474C] hover:text-[#0F1C2E] transition-colors tracking-wide">
              Frameworks
            </a>
            <a href="#how-it-works" className="text-sm font-semibold text-[#44474C] hover:text-[#0F1C2E] transition-colors tracking-wide">
              How it works
            </a>
          </nav>
          <Link
            href="/app"
            className="bg-[#0F1C2E] text-white text-sm font-semibold px-5 py-2.5 rounded hover:bg-[#1B3A5C] transition-colors"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-[#0F1C2E] text-white py-24 md:py-32 relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-8 grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h1 className="text-4xl md:text-5xl font-bold leading-tight tracking-tight">
              Legal compliance<br />simplified through<br />AI precision.
            </h1>
            <p className="text-[#BAC7DF] text-lg leading-relaxed max-w-md">
              Navigate Australian regulatory standards. Upload documents, identify gaps, and ensure compliance with institutional-grade AI analysis.
            </p>
            <div className="flex gap-4 pt-2">
              <Link
                href="/app"
                className="bg-white text-[#0F1C2E] font-semibold px-6 py-3 rounded hover:bg-[#D6E3FC] transition-colors"
              >
                Launch App
              </Link>
            </div>
          </div>
          {/* Mock dashboard preview */}
          <div className="hidden md:block">
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div className="bg-[#1B3A5C] rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#BAC7DF] uppercase tracking-wide">Compliance Score</span>
                  <span className="text-xs text-green-400 font-semibold">Low Risk</span>
                </div>
                <div className="text-4xl font-bold text-white">84<span className="text-xl text-[#BAC7DF]">/100</span></div>
                <div className="w-full bg-white/10 rounded-full h-1.5">
                  <div className="bg-[#D6E3FC] h-1.5 rounded-full" style={{ width: "84%" }} />
                </div>
              </div>
              <div className="mt-3 space-y-2">
                {["Privacy Act 1988 — 2 gaps found", "Fair Work Act 2009 — Compliant", "WHS Act 2011 — 1 gap found"].map((item) => (
                  <div key={item} className="bg-white/5 border border-white/10 rounded px-3 py-2 text-xs text-[#BAC7DF]">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-[#F8F9FF]">
        <div className="max-w-6xl mx-auto px-8">
          <div className="mb-12">
            <span className="text-xs font-semibold uppercase tracking-widest text-[#44474C]">Core Capabilities</span>
            <h2 className="text-2xl font-bold text-[#0B1C30] mt-2">Precision-engineered for Australian law.</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: "📄",
                title: "Upload Documents",
                desc: "Securely upload PDF or DOCX compliance documents. The AI parses, chunks, and indexes them for instant retrieval.",
                tag: "PDF & DOCX",
              },
              {
                icon: "💬",
                title: "Ask Questions",
                desc: "Ask plain English questions about your obligations. Get structured answers backed by your documents and live legislation.",
                tag: "LLM Powered",
              },
              {
                icon: "🔍",
                title: "Find Gaps",
                desc: "Automatically identify where your internal policies fall short of Australian legal requirements — clause by clause.",
                tag: "Gap Analysis",
              },
            ].map((f) => (
              <div key={f.title} className="bg-white border border-[#C5C6CD] rounded-xl p-6 flex flex-col gap-4 hover:shadow-sm transition-shadow">
                <div className="text-3xl">{f.icon}</div>
                <div>
                  <h3 className="font-semibold text-lg text-[#0B1C30] mb-2">{f.title}</h3>
                  <p className="text-sm text-[#44474C] leading-relaxed">{f.desc}</p>
                </div>
                <div className="mt-auto pt-4 border-t border-[#E5E7EB] flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#0F1C2E]">{f.tag}</span>
                  <span className="text-[#C5C6CD]">→</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Frameworks */}
      <section id="frameworks" className="py-20 bg-[#EFF4FF]">
        <div className="max-w-6xl mx-auto px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="grid grid-cols-2 gap-4">
              {FRAMEWORKS.map((f) => (
                <div key={f.code} className="bg-white border border-[#C5C6CD] rounded-lg p-4 text-center">
                  <span className="block text-base font-bold text-[#0F1C2E]">{f.code}</span>
                  <span className="text-xs text-[#44474C]">{f.sub}</span>
                </div>
              ))}
            </div>
            <div className="space-y-5">
              <h2 className="text-3xl font-bold text-[#0B1C30]">Stay aligned with evolving standards.</h2>
              <p className="text-[#44474C] leading-relaxed">
                ComplyAU is trained on and continuously checked against current Australian regulatory frameworks. From the Privacy Act to the Fair Work Act, we ensure your organisation is analysed against what matters.
              </p>
              <ul className="space-y-3">
                {[
                  "Live legislation fetching from government sources",
                  "Cross-document gap identification",
                  "Severity-ranked compliance scoring",
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-sm font-medium text-[#0B1C30]">
                    <span className="text-[#0F1C2E]">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-20 bg-[#F8F9FF]">
        <div className="max-w-3xl mx-auto px-8">
          <h2 className="text-2xl font-bold text-center text-[#0B1C30] mb-14">How it works</h2>
          <div className="space-y-10">
            {[
              { step: "01", title: "Upload your compliance documents", desc: "Drop in your PDF or DOCX files. ComplyAU parses, chunks, and indexes them automatically." },
              { step: "02", title: "Ask a compliance question", desc: "Type any question about your obligations. The AI searches your documents and live Australian legislation." },
              { step: "03", title: "Get a gap analysis and score", desc: "Receive a detailed compliance report — what your policy says, what the law requires, and a score out of 100." },
            ].map((s) => (
              <div key={s.step} className="flex gap-6">
                <div className="text-3xl font-bold text-[#C5C6CD] w-12 shrink-0">{s.step}</div>
                <div>
                  <h3 className="font-semibold mb-1 text-[#0B1C30]">{s.title}</h3>
                  <p className="text-sm text-[#44474C] leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-[#0F1C2E] py-20 px-8 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-white mb-4">Ready to check your compliance?</h2>
          <p className="text-[#BAC7DF] mb-8">No account required. Upload a document and get started in seconds.</p>
          <Link
            href="/app"
            className="bg-white text-[#0F1C2E] font-semibold px-8 py-3 rounded hover:bg-[#D6E3FC] transition-colors inline-block"
          >
            Launch App →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0F1C2E] border-t border-white/10 px-8 py-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <span className="font-semibold text-white">ComplyAU</span>
          <p className="text-sm text-[#78849B]">© {new Date().getFullYear()} ComplyAU. Built for Australian businesses.</p>
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