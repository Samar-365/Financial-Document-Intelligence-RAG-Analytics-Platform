"use client";

import React, { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Citation } from "@/types/rag";
import {
  X,
  BookOpen,
  FileText,
  Percent,
  Copy,
  Check,
  ShieldCheck,
  Quote,
} from "lucide-react";

interface CitationDrawerProps {
  citation: Citation | null;
  isOpen: boolean;
  onClose: () => void;
  documentName?: string;
}

function getRelevanceMeta(score: number) {
  const pct = Math.round(score * 100);
  if (score >= 0.8) {
    return {
      label: "High Match",
      textClass: "text-emerald-400",
      bgClass: "bg-emerald-500",
      borderClass: "border-emerald-500/30",
    };
  }
  if (score >= 0.6) {
    return {
      label: "Moderate Match",
      textClass: "text-[#FFA8B2]",
      bgClass: "bg-[#E63946]",
      borderClass: "border-[rgba(230,57,70,0.4)]",
    };
  }
  return {
    label: "Low Match",
    textClass: "text-amber-400",
    bgClass: "bg-amber-500",
    borderClass: "border-amber-500/30",
  };
}

export function CitationDrawer({
  citation,
  isOpen,
  onClose,
  documentName,
}: CitationDrawerProps) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  const copySnippet = () => {
    if (!citation?.snippet) return;
    navigator.clipboard.writeText(citation.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen && !citation) return null;

  const relevance = citation ? getRelevanceMeta(citation.relevance_score) : null;
  const pct = citation ? Math.min(100, Math.max(0, Math.round(citation.relevance_score * 100))) : 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity duration-300",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Citation Source Inspector"
        className={cn(
          "fixed right-0 top-0 z-50 h-full w-full max-w-md md:max-w-lg",
          "border-l border-[rgba(184,29,36,0.28)] bg-[#0D0C12] shadow-2xl backdrop-blur-2xl",
          "flex flex-col transition-transform duration-300 ease-in-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[rgba(184,29,36,0.25)] px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(184,29,36,0.2)] border border-[rgba(230,57,70,0.45)] text-[#E63946]">
              <Quote className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                Grounding Source Citation
              </h3>
              <p className="text-xs text-[#94A3B8]">
                Verifiable extraction chunk from source filing
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[rgba(196,30,58,0.3)] bg-[#111017] text-slate-400 hover:text-white hover:border-[#E63946] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        {citation && (
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Filing provenance badge */}
            <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-4 shadow-md">
              <div className="flex items-center gap-2 text-xs text-[#94A3B8] mb-2">
                <FileText className="h-3.5 w-3.5 text-[#E63946]" />
                <span className="font-bold uppercase tracking-wider text-[11px] text-slate-300">
                  Source Document
                </span>
              </div>
              <p className="text-sm font-semibold text-white truncate">
                {documentName || citation.doc_title || "Financial Annual Report"}
              </p>
              <div className="mt-3 flex items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-[rgba(184,29,36,0.2)] border border-[rgba(230,57,70,0.45)] text-[#FFA8B2] text-xs font-bold">
                  <BookOpen className="h-3 w-3" />
                  Page {citation.page_number}
                </span>
                {citation.chunk_index !== undefined && (
                  <span className="inline-flex items-center px-2 py-1 rounded-md bg-[#161522] border border-white/5 text-slate-300 text-xs font-mono">
                    Chunk #{citation.chunk_index}
                  </span>
                )}
                {citation.section && (
                  <span className="inline-flex items-center px-2 py-1 rounded-md bg-[#161522] text-slate-400 text-xs truncate max-w-[180px]">
                    {citation.section}
                  </span>
                )}
              </div>
            </div>

            {/* Relevance Score Card */}
            {relevance && (
              <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-4 shadow-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 text-xs text-[#94A3B8]">
                    <Percent className="h-3.5 w-3.5 text-[#E63946]" />
                    <span className="font-bold uppercase tracking-wider text-[11px] text-slate-300">
                      Vector Similarity Match
                    </span>
                  </div>
                  <span className={cn("text-xs font-bold px-2 py-0.5 rounded-full border", relevance.borderClass, relevance.textClass)}>
                    {pct}% • {relevance.label}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#181622] overflow-hidden">
                  <div
                    className={cn("h-full rounded-full transition-all duration-500", relevance.bgClass)}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <p className="text-[11px] text-slate-400 mt-2">
                  Calculated using dense 384-dimensional cosine distance against the pgvector HNSW index.
                </p>
              </div>
            )}

            {/* Verbatim Excerpt */}
            <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-4 space-y-3 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <Quote className="h-3.5 w-3.5 text-[#E63946]" />
                  Verbatim Filing Snippet
                </span>
                <button
                  onClick={copySnippet}
                  className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-2.5 py-1 rounded-md bg-[#181622] border border-[rgba(196,30,58,0.3)] hover:border-[#E63946] transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-emerald-400 font-bold">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>

              <div className="rounded-lg border border-[rgba(184,29,36,0.25)] bg-[rgba(184,29,36,0.08)] p-4 text-sm leading-relaxed text-[#F1F5F9] font-serif italic selection:bg-[#E63946]/40">
                &ldquo;{citation.snippet}&rdquo;
              </div>
            </div>

            {/* Ind AS & Audit Grounding Notice */}
            <div className="rounded-xl border border-[rgba(196,30,58,0.28)] bg-[rgba(184,29,36,0.1)] p-4 flex gap-3">
              <ShieldCheck className="h-5 w-5 text-[#E63946] shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <p className="font-bold text-white">Auditable Evidence Trail</p>
                <p className="text-[#94A3B8] leading-relaxed">
                  FinDoc groundings are deterministic extracts tagged with document and page provenance. The AI analyst is strictly constrained by negative prompt formulation to prevent numeric hallucination.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-[rgba(184,29,36,0.25)] px-6 py-3 flex items-center justify-between bg-[#08080A]">
          <p className="text-xs text-slate-500">Press ESC to dismiss</p>
          <button
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-[#E63946] font-semibold"
          >
            Close esc
          </button>
        </div>
      </div>
    </>
  );
}
