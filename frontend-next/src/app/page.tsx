"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  FileText,
  Activity,
  ShieldCheck,
  Layers,
  TrendingUp,
  GitCompare,
  Database,
  Cpu,
  Bot,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen w-full bg-white text-black antialiased font-sans selection:bg-[#FF0000] selection:text-white">
      {/* ── Top Navigation Bar (Exaggerated Minimalism) ── */}
      <header className="fixed top-0 left-0 right-0 z-50 flex h-20 items-center justify-between px-6 md:px-12 bg-white/95 backdrop-blur-md border-b border-black">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center bg-black text-white font-black text-sm tracking-tighter transition-transform group-hover:bg-[#FF0000]">
            FD
          </div>
          <span className="font-black text-xl tracking-tighter text-black uppercase">
            FINDOC
          </span>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-mono font-bold uppercase tracking-widest text-black">
          <Link href="#statements" className="hover:text-[#FF0000] transition-colors">
            Statements
          </Link>
          <Link href="#capabilities" className="hover:text-[#FF0000] transition-colors">
            Capabilities
          </Link>
        </nav>

        {/* Right CTA */}
        <div className="flex items-center gap-4">
          <Link href="/documents">
            <button className="hidden sm:inline-flex px-4 py-2 text-xs font-mono font-bold uppercase tracking-wider border border-black bg-white hover:bg-black hover:text-white transition-all cursor-pointer">
              [ Ingest Filing ]
            </button>
          </Link>
          <Link href="/dashboard">
            <button className="px-5 py-2 text-xs font-mono font-bold uppercase tracking-wider bg-black text-white hover:bg-[#FF0000] transition-all cursor-pointer">
              Workspace →
            </button>
          </Link>
        </div>
      </header>

      {/* ── 1. MONUMENTAL STATEMENT HERO SECTION ── */}
      <section className="relative pt-36 pb-20 md:pt-48 md:pb-28 px-6 md:px-12 border-b border-black">
        <div className="max-w-7xl mx-auto">
          {/* Monumental Typography: Solid Black + Hollow Outline Text */}
          <div className="mb-12">
            <h1 className="text-6xl sm:text-8xl lg:text-[112px] font-black tracking-tighter uppercase leading-[0.88] text-black">
              FINANCIAL
            </h1>
            <h1 className="text-6xl sm:text-8xl lg:text-[112px] font-black tracking-tighter uppercase leading-[0.88] text-black">
              INTELLIGENCE
            </h1>
            <h1 className="text-6xl sm:text-8xl lg:text-[112px] font-black tracking-tighter uppercase leading-[0.88] stroke-text-thick">
              UNLOCKED.
            </h1>
          </div>

          {/* Subtitle & Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end pt-6 border-t border-black/10">
            <div className="lg:col-span-7">
              <p className="text-lg sm:text-xl font-medium text-neutral-800 leading-relaxed max-w-2xl">
                Transform complex corporate disclosures, Ind AS filings, and balance sheets into deterministic financial metrics, corporate solvency scores, and verified vector answers.
              </p>
            </div>

            <div className="lg:col-span-5 flex flex-wrap items-center gap-4 lg:justify-end">
              <Link href="/dashboard">
                <button className="h-12 px-8 text-xs font-mono font-black uppercase tracking-widest bg-black text-white hover:bg-[#FF0000] transition-all shadow-[4px_4px_0px_#000000] hover:shadow-none hover:translate-x-1 hover:translate-y-1 cursor-pointer">
                  Enter Workspace →
                </button>
              </Link>
              <Link href="/documents">
                <button className="h-12 px-7 text-xs font-mono font-black uppercase tracking-widest border border-black bg-white text-black hover:bg-black hover:text-white transition-all cursor-pointer">
                  Ingest Filing
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. ARCHITECTURAL METRICS STRIP ── */}
      <section className="border-b border-black bg-neutral-50">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-black">
          {[
            { num: "01", label: "STANDARDS", val: "Ind AS & US GAAP" },
            { num: "02", label: "RETRIEVAL", val: "pgvector HNSW" },
            { num: "03", label: "EVIDENCE", val: "Page Citations" },
            { num: "04", label: "ACCURACY", val: "Deterministic" },
          ].map((item, idx) => (
            <div key={idx} className="p-6 md:p-8 flex flex-col justify-between">
              <span className="text-xs font-mono font-bold text-neutral-400 mb-2">
                [ {item.num} / {item.label} ]
              </span>
              <span className="text-lg md:text-xl font-black uppercase tracking-tight text-black">
                {item.val}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ── 3. FINANCIAL STATEMENTS SHOWCASE (HIGH CONTRAST EDITORIAL) ── */}
      <section id="statements" className="py-24 px-6 md:px-12 border-b border-black bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-16 pb-6 border-b border-black">
            <div>
              <h2 className="text-4xl sm:text-6xl font-black uppercase tracking-tighter text-black leading-none">
                FINANCIAL STATEMENTS
              </h2>
            </div>
            <p className="text-sm font-mono uppercase text-neutral-500 max-w-md">
              Extract tabular balance sheets, income statements, and cash flows with zero parsing drift.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                code: "01",
                title: "Balance Sheet",
                file: "Balance Sheet.png",
                desc: "Assets, liabilities, equity structure, and working capital ratios.",
              },
              {
                code: "02",
                title: "Cash Flow Statement",
                file: "Cash Flow Statement.png",
                desc: "Operating cash quality, capital expenditure, and free cash flows.",
              },
              {
                code: "03",
                title: "Income Statement",
                file: "Income Statement.png",
                desc: "Revenue growth, operating margins, EBITDA, and net earnings.",
              },
              {
                code: "04",
                title: "Auditor's Report",
                file: "Independent Auditor's Report.png",
                desc: "Audit opinions, key audit matters (KAMs), and risk disclosures.",
              },
            ].map((doc, idx) => (
              <div
                key={idx}
                className="group border border-black bg-white p-6 rounded-none transition-all duration-150 hover:shadow-[6px_6px_0px_#000000] hover:-translate-x-1 hover:-translate-y-1 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-black/10 mb-4">
                    <span className="font-mono text-xs font-black text-neutral-400">
                      [ {doc.code} ]
                    </span>
                    <ArrowUpRight className="h-4 w-4 text-black group-hover:text-[#FF0000] transition-colors" />
                  </div>

                  <div className="relative aspect-[4/3] w-full border border-black overflow-hidden mb-5 bg-neutral-100">
                    <Image
                      src={`/${doc.file}`}
                      alt={doc.title}
                      fill
                      sizes="(max-width: 768px) 100vw, 25vw"
                      className="object-cover object-top filter grayscale contrast-125 group-hover:grayscale-0 transition-all duration-200"
                    />
                  </div>

                  <h3 className="font-black text-lg uppercase tracking-tight text-black mb-2">
                    {doc.title}
                  </h3>
                  <p className="text-xs text-neutral-600 leading-relaxed font-sans mb-6">
                    {doc.desc}
                  </p>
                </div>

                <Link
                  href="/analysis"
                  className="inline-flex items-center gap-1 font-mono text-xs font-black uppercase tracking-wider text-black group-hover:text-[#FF0000] transition-colors pt-3 border-t border-black/10"
                >
                  <span>Explore Line Items</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. CAPABILITIES PIPELINE ── */}
      <section id="capabilities" className="py-24 px-6 md:px-12 border-b border-black bg-neutral-50">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16 pb-6 border-b border-black">
            <h2 className="text-4xl sm:text-6xl font-black uppercase tracking-tighter text-black leading-none">
              ENTERPRISE CAPABILITIES
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                code: "01",
                icon: Layers,
                title: "Ind AS & GAAP Extraction",
                desc: "Deterministic parsing of Indian Accounting Standards (Ind AS) and US GAAP tabular disclosures with line-item reconciliation.",
              },
              {
                code: "02",
                icon: TrendingUp,
                title: "5D Health Scoring",
                desc: "Automated scoring across Solvency, Liquidity, Profitability, Leverage, and Operational Efficiency with benchmark gates.",
              },
              {
                code: "03",
                icon: Bot,
                title: "Auditable RAG Assistant",
                desc: "Natural language query synthesis directly linked to verified page-level source chunks in the PDF filing.",
              },
              {
                code: "04",
                icon: GitCompare,
                title: "Entity Benchmarking",
                desc: "Side-by-side variance analysis comparing two corporate filings with percentage delta breakdowns.",
              },
              {
                code: "05",
                icon: ShieldCheck,
                title: "Footnote Risk Detection",
                desc: "Identifies debt covenant violations, pending legal proceedings, and contingent liabilities in report footnotes.",
              },
              {
                code: "06",
                icon: Cpu,
                title: "Telemetry & Logs",
                desc: "Complete observability into extraction latency, vector similarity metrics, and database health.",
              },
            ].map((cap, i) => (
              <div
                key={i}
                className="border border-black bg-white p-8 rounded-none transition-all duration-150 hover:shadow-[6px_6px_0px_#000000] hover:-translate-x-1 hover:-translate-y-1 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between pb-4 border-b border-black/10 mb-6">
                    <span className="font-mono text-xs font-black text-neutral-400">
                      [ {cap.code} ]
                    </span>
                    <div className="h-8 w-8 border border-black bg-black text-white flex items-center justify-center">
                      <cap.icon className="h-4 w-4" />
                    </div>
                  </div>
                  <h3 className="font-black text-xl uppercase tracking-tight text-black mb-3">
                    {cap.title}
                  </h3>
                  <p className="text-sm text-neutral-600 leading-relaxed font-sans">
                    {cap.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. STATEMENT CTA BAR ── */}
      <section className="py-20 px-6 md:px-12 bg-black text-white border-b border-black">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
          <div>
            <span className="text-xs font-mono font-bold text-[#FF0000] uppercase tracking-widest mb-2 block">
              [ READY TO BEGIN ]
            </span>
            <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tighter leading-none">
              ANALYZE YOUR FIRST CORPORATE FILING
            </h2>
          </div>
          <Link href="/documents">
            <button className="h-14 px-10 text-xs font-mono font-black uppercase tracking-widest bg-white text-black hover:bg-[#FF0000] hover:text-white transition-all cursor-pointer">
              Upload Document →
            </button>
          </Link>
        </div>
      </section>

      {/* ── 6. MINIMALIST FOOTER ── */}
      <footer className="py-12 px-6 md:px-12 bg-white text-xs font-mono uppercase text-black">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="h-6 w-6 bg-black text-white font-black text-[10px] flex items-center justify-center">
              FD
            </div>
            <span className="font-black tracking-tight">FINDOC INTELLIGENCE</span>
            <span className="text-neutral-400">•</span>
            <span className="text-neutral-500">EXAGGERATED MINIMALISM</span>
          </div>

          <div className="flex items-center gap-6 font-bold">
            <Link href="/dashboard" className="hover:text-[#FF0000] transition-colors">
              [ Workspace ]
            </Link>
            <Link href="/documents" className="hover:text-[#FF0000] transition-colors">
              [ Ingestion ]
            </Link>
            <Link href="/analysis" className="hover:text-[#FF0000] transition-colors">
              [ Analysis ]
            </Link>
            <Link href="/audit" className="hover:text-[#FF0000] transition-colors">
              [ Telemetry ]
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
