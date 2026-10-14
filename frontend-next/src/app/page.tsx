"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Activity,
  FileText,
  PieChart,
  Bot,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Database,
  Cpu,
  Sparkles,
  Layers,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen w-full bg-[#08080A] text-slate-100 antialiased font-sans overflow-x-hidden selection:bg-[#E63946]/40 selection:text-white">
      {/* ── Top Navigation Bar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex h-20 items-center justify-between px-6 md:px-12 backdrop-blur-xl bg-[#08080A]/80 border-b border-[rgba(184,29,36,0.2)]">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.2)] border border-[rgba(230,57,70,0.55)] shadow-[0_0_15px_rgba(230,57,70,0.3)] group-hover:scale-105 transition-all">
            <Activity className="h-5 w-5 text-[#E63946]" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-xl tracking-tight text-white leading-none">
              Fin<span className="text-[#E63946]">Doc</span>
            </span>
            <span className="text-[9px] uppercase font-bold tracking-[0.1em] text-[#94A3B8] mt-1">
              Financial Intelligence
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-4">
          <Link href="/documents">
            <Button variant="outline" size="sm" className="hidden sm:inline-flex text-xs">
              Ingest Document
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="gradient" size="sm" className="gap-2 text-xs">
              <span>Open Workspace</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* ── 1. CINEMATIC ENTERPRISE HERO SECTION ── */}
      <section className="relative pt-36 pb-20 md:pt-44 md:pb-28 flex flex-col items-center justify-center text-center px-4 overflow-hidden min-h-[90vh]">
        {/* Vertical Volumetric Laser Beam matching Streamlit laser_flow.py */}
        <div className="laser-beam" />
        
        {/* Radial Background Diffuse Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-gradient-to-b from-[#E63946]/20 via-[#B81D24]/10 to-transparent blur-[120px] pointer-events-none" />

        {/* Floating Pill Badge */}
        <div className="relative z-10 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[rgba(230,57,70,0.4)] bg-[#111017]/90 shadow-[0_0_20px_rgba(230,57,70,0.25)] text-xs font-semibold text-slate-200 mb-8 backdrop-blur-md animate-in fade-in slide-in-from-top-4 duration-700">
          <span className="flex h-2 w-2 rounded-full bg-[#E63946] animate-ping" />
          <span className="text-white font-bold">FinDoc Intelligence Layer</span>
          <span className="text-slate-500">•</span>
          <span className="text-[#FFA8B2]">Next.js 15 & pgvector HNSW</span>
        </div>

        {/* Main Headline */}
        <h1 className="relative z-10 max-w-4xl text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.15] mb-6">
          Autonomous Financial Document Intelligence &{" "}
          <span className="bg-gradient-to-r from-white via-[#FFA8B2] to-[#E63946] bg-clip-text text-transparent">
            RAG Analytics
          </span>
        </h1>

        {/* Subtitle */}
        <p className="relative z-10 max-w-2xl text-sm sm:text-base md:text-lg text-[#94A3B8] leading-relaxed mb-10">
          Transform complex corporate PDF disclosures, Ind AS filings, and balance sheets into structured financial metrics, corporate solvency scores, and auditable answers.
        </p>

        {/* Primary CTA Buttons */}
        <div className="relative z-10 flex flex-wrap items-center justify-center gap-4 mb-16">
          <Link href="/dashboard">
            <Button
              variant="gradient"
              size="lg"
              className="h-12 px-8 text-sm gap-2.5 shadow-2xl"
            >
              <span>Open Financial Workspace</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/documents">
            <Button
              variant="outline"
              size="lg"
              className="h-12 px-7 text-sm gap-2"
            >
              <FileText className="h-4 w-4 text-[#E63946]" />
              <span>Ingest Filing (PDF / Excel)</span>
            </Button>
          </Link>
        </div>

        {/* 4 Floating Statement Cards (Balance Sheet, Cash Flow, Income Statement, Audit Report) */}
        <div className="relative z-10 grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl w-full px-4 mt-6">
          {[
            {
              title: "Balance Sheet",
              file: "Balance Sheet.png",
              desc: "Assets, Equity & Debt Obligations",
            },
            {
              title: "Cash Flow Statement",
              file: "Cash Flow Statement.png",
              desc: "Operating Cash Quality & Free Cash Flow",
            },
            {
              title: "Income Statement",
              file: "Income Statement.png",
              desc: "EBITDA, OPM & PAT Margins",
            },
            {
              title: "Auditor's Report",
              file: "Independent Auditor's Report.png",
              desc: "Audit Opinion & Risk Disclosures",
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="group overflow-hidden rounded-2xl border border-[rgba(196,30,58,0.28)] bg-[#111017]/90 shadow-[0_4px_20px_rgba(0,0,0,0.6)] backdrop-blur-md transition-all duration-300 hover:border-[#E63946] hover:shadow-[0_8px_30px_rgba(230,57,70,0.25)] hover:-translate-y-1 text-left flex flex-col"
            >
              <div className="relative h-32 w-full bg-[#181622] overflow-hidden">
                <Image
                  src={`/${item.file}`}
                  alt={item.title}
                  fill
                  className="object-cover opacity-60 group-hover:opacity-90 group-hover:scale-105 transition-all duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#111017] via-transparent to-transparent" />
              </div>
              <div className="p-4 flex-1 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#E63946] mb-1">
                    Ind AS Line Item
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#FFA8B2] transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-xs text-[#94A3B8] mt-1 leading-normal">
                    {item.desc}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── 2. CORE CAPABILITIES (Streamlit Theme Matching) ── */}
      <section className="relative py-20 px-6 md:px-12 max-w-7xl mx-auto border-t border-[rgba(184,29,36,0.25)]">
        <div className="text-center mb-16">
          <div className="text-xs font-bold uppercase tracking-[0.1em] text-[#E63946] mb-2">
            CORE CAPABILITIES
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            One intelligence layer for complex financial filings.
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto mt-2 leading-relaxed">
            Transform lengthy disclosures and spreadsheets into structured indicators, solvency ratings, and verifiable answers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Capability 1 */}
          <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-8 shadow-[0_4px_20px_rgba(0,0,0,0.5)] hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_6px_24px_rgba(184,29,36,0.18)] transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.15)] border border-[rgba(230,57,70,0.3)] text-[#E63946] mb-6">
              <FileText className="h-6 w-6" />
            </div>
            <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[#E63946] mb-2">
              INGESTION
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Multi-Format Ingestion</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Ingest corporate PDFs, annual reports, 10-K/10-Q filings, spreadsheets (CSV, Excel), and balance sheets into clean, structured tables without manual re-keying.
            </p>
          </div>

          {/* Capability 2 */}
          <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-8 shadow-[0_4px_20px_rgba(0,0,0,0.5)] hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_6px_24px_rgba(184,29,36,0.18)] transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.15)] border border-[rgba(230,57,70,0.3)] text-[#E63946] mb-6">
              <PieChart className="h-6 w-6" />
            </div>
            <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[#E63946] mb-2">
              EVALUATION
            </div>
            <h3 className="text-lg font-bold text-white mb-2">5D Financial Health</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Automatically extract 12 core line items, compute ratios, and assess corporate solvency across Growth, Profitability, Liquidity, Leverage, and Cash Flow.
            </p>
          </div>

          {/* Capability 3 */}
          <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-8 shadow-[0_4px_20px_rgba(0,0,0,0.5)] hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_6px_24px_rgba(184,29,36,0.18)] transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.15)] border border-[rgba(230,57,70,0.3)] text-[#E63946] mb-6">
              <Bot className="h-6 w-6" />
            </div>
            <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[#E63946] mb-2">
              VERIFICATION
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Audit-Grounded Inquiry</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Explore questions conversationally with exact page-level citations and verbatim excerpts from source filings for complete transparency.
            </p>
          </div>
        </div>
      </section>

      {/* ── 3. WORKFLOW PIPELINE ── */}
      <section className="py-20 px-6 md:px-12 max-w-7xl mx-auto border-t border-[rgba(184,29,36,0.25)]">
        <div className="text-center mb-16">
          <div className="text-xs font-bold uppercase tracking-[0.1em] text-[#E63946] mb-2">
            ARCHITECTURE
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Minimal 4-Stage Extraction & RAG Pipeline
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              step: "01",
              title: "Boundary & Ingestion",
              desc: "Magic-byte validation (%PDF-1.x) with strict 50MB limits.",
              icon: FileText,
            },
            {
              step: "02",
              title: "Table Integrity Lock",
              desc: "Preserves tabular structure with 150-char backward overlap.",
              icon: Layers,
            },
            {
              step: "03",
              title: "pgvector HNSW Index",
              desc: "384-dim dense embeddings with cosine similarity metric.",
              icon: Database,
            },
            {
              step: "04",
              title: "Deterministic RAG",
              desc: "Strict negative constraint prompt prevents hallucination.",
              icon: ShieldCheck,
            },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-6 shadow-md relative group hover:border-[#E63946] transition-all"
              >
                <div className="text-2xl font-black text-[#E63946]/40 mb-3 font-mono">
                  {item.step}
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <Icon className="h-4 w-4 text-[#E63946]" />
                  <h3 className="text-sm font-bold text-white">{item.title}</h3>
                </div>
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  {item.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── 4. FOOTER ── */}
      <footer className="border-t border-[rgba(184,29,36,0.25)] bg-[#0D0C12] py-12 px-6 md:px-12 text-center text-xs text-slate-500">
        <div className="flex items-center justify-center gap-2 mb-3">
          <Activity className="h-4 w-4 text-[#E63946]" />
          <span className="font-extrabold text-white text-sm">
            Fin<span className="text-[#E63946]">Doc</span> Platform
          </span>
        </div>
        <p className="max-w-md mx-auto text-slate-400 text-[11px] mb-4">
          Autonomous financial disclosure intelligence, corporate health scoring, and verifiable RAG analytics.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 text-[11px] text-[#FFA8B2]">
          <span>Air-Gapped Local Inference</span>
          <span>•</span>
          <span>Zero Extrapolation Constraint</span>
          <span>•</span>
          <span>Ind AS / IFRS Compatible</span>
        </div>
      </footer>
    </div>
  );
}
