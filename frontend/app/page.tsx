import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-[#0F1C2E] text-white px-8 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">ComplyAU</span>
        <div className="flex items-center gap-6">
          <a href="#features" className="text-sm text-gray-300 hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="text-sm text-gray-300 hover:text-white transition-colors">How it works</a>
          <Link
            href="/app"
            className="bg-white text-[#0F1C2E] text-sm font-medium px-4 py-2 rounded hover:bg-gray-100 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-[#0F1C2E] text-white px-8 py-24 text-center">
        <div className="max-w-3xl mx-auto">
          <span className="inline-block bg-[#1B3A5C] text-blue-200 text-xs font-medium px-3 py-1 rounded-full mb-6 tracking-wide uppercase">
            Australian Compliance
          </span>
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
            Know if your business is<br />compliant with Australian law
          </h1>
          <p className="text-gray-300 text-lg mb-10 max-w-xl mx-auto">
            Upload your compliance documents, ask a question, and get an instant AI-powered gap analysis against the Privacy Act, Fair Work Act, and more.
          </p>
          <Link
            href="/app"
            className="bg-white text-[#0F1C2E] font-semibold px-8 py-3 rounded hover:bg-gray-100 transition-colors inline-block"
          >
            Try it free →
          </Link>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-8 bg-white">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-14 text-[#1A1A2E]">
            Everything you need for compliance analysis
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Upload Documents",
                desc: "Upload your privacy policies, employee handbooks, and compliance documents in PDF or DOCX format.",
                icon: "📄",
              },
              {
                title: "Ask Questions",
                desc: "Ask plain English questions like 'Are we compliant with the Privacy Act?' and get structured answers.",
                icon: "💬",
              },
              {
                title: "Find Gaps",
                desc: "Instantly identify where your internal policies fall short of Australian legal requirements.",
                icon: "🔍",
              },
            ].map((f) => (
              <div key={f.title} className="border border-[#E5E7EB] rounded-lg p-6">
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                <p className="text-[#6B7280] text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-20 px-8 bg-[#F8F9FA]">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-14 text-[#1A1A2E]">How it works</h2>
          <div className="space-y-8">
            {[
              { step: "01", title: "Upload your compliance documents", desc: "Drag and drop your PDF or DOCX files. ComplyAU parses, chunks, and indexes them automatically." },
              { step: "02", title: "Ask a compliance question", desc: "Type any question about your obligations. The AI agent searches your documents and live Australian legislation." },
              { step: "03", title: "Get a structured gap analysis", desc: "Receive a detailed report with what your policy says, what the law requires, and exactly where the gaps are." },
            ].map((s) => (
              <div key={s.step} className="flex gap-6">
                <div className="text-3xl font-bold text-[#E5E7EB] w-12 shrink-0">{s.step}</div>
                <div>
                  <h3 className="font-semibold mb-1">{s.title}</h3>
                  <p className="text-[#6B7280] text-sm leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-[#0F1C2E] text-white py-16 px-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to check your compliance?</h2>
        <p className="text-gray-300 mb-8">No account required. Upload a document and get started in seconds.</p>
        <Link
          href="/app"
          className="bg-white text-[#0F1C2E] font-semibold px-8 py-3 rounded hover:bg-gray-100 transition-colors inline-block"
        >
          Get Started →
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#E5E7EB] px-8 py-6 text-center text-sm text-[#6B7280]">
        © {new Date().getFullYear()} ComplyAU. Built for Australian businesses.
      </footer>
    </div>
  );
}