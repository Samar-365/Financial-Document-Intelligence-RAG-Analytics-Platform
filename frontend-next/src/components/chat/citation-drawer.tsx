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
import { Button } from "@/components/ui/button";

interface CitationDrawerProps {
  citation: Citation | null;
  isOpen: boolean;
  onClose: () => void;
  documentName?: string;
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

  const pct = citation ? Math.min(100, Math.max(0, Math.round(citation.relevance_score * 100))) : 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/60 transition-opacity duration-200",
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
          "border-l-2 border-black bg-white shadow-[-8px_0px_0px_#000000]",
          "flex flex-col transition-transform duration-200 ease-in-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-black p-5 bg-white">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center border border-black bg-black text-white shrink-0">
              <Quote className="h-4 w-4 text-[#FF0000]" />
            </div>
            <div>
              <h3 className="text-xs font-black uppercase tracking-wider text-black">
                GROUNDING SOURCE CITATION
              </h3>
              <p className="text-[10px] font-mono text-zinc-600 uppercase">
                VERIFIABLE EXTRACT FROM FILING CORPUS
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center border border-black bg-white text-black hover:bg-black hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        {citation && (
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Filing provenance badge */}
            <div className="border border-black bg-white p-5 shadow-[4px_4px_0px_#000000]">
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-600 mb-2 border-b border-black pb-1.5">
                <FileText className="h-3.5 w-3.5 text-black" />
                <span className="font-bold uppercase tracking-wider">SOURCE DOCUMENT</span>
              </div>
              <p className="text-sm font-black uppercase text-black truncate">
                {documentName || citation.doc_title || "Financial Annual Report"}
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 border border-black bg-black text-white px-2.5 py-1 text-xs font-mono font-bold uppercase">
                  <BookOpen className="h-3 w-3 text-[#FF0000]" />
                  PAGE {citation.page_number}
                </span>
                {citation.chunk_index !== undefined && (
                  <span className="inline-flex items-center border border-black bg-white text-black px-2 py-1 text-xs font-mono font-bold uppercase">
                    CHUNK #{citation.chunk_index}
                  </span>
                )}
                {citation.section && (
                  <span className="inline-flex items-center border border-black bg-zinc-100 text-black px-2 py-1 text-xs font-mono uppercase truncate max-w-[200px]">
                    {citation.section}
                  </span>
                )}
              </div>
            </div>

            {/* Relevance Score Card */}
            <div className="border border-black bg-white p-5 shadow-[4px_4px_0px_#000000]">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-black uppercase">
                  <Percent className="h-3.5 w-3.5 text-black" />
                  <span>VECTOR SIMILARITY COSINE MATCH</span>
                </div>
                <span className="text-xs font-mono font-black uppercase border border-black bg-black text-white px-2 py-0.5">
                  {pct}% MATCH
                </span>
              </div>
              <div className="h-2 w-full border border-black bg-zinc-100 p-0.5">
                <div
                  className="h-full bg-black transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <p className="text-[10px] font-mono text-zinc-600 mt-2 uppercase">
                CALCULATED VIA DENSE 1536-DIMENSIONAL COSINE PROXIMITY AGAINST POSTGRESQL PGVECTOR.
              </p>
            </div>

            {/* Verbatim Excerpt */}
            <div className="border border-black bg-white p-5 space-y-3 shadow-[4px_4px_0px_#000000]">
              <div className="flex items-center justify-between border-b border-black pb-2">
                <span className="text-xs font-black uppercase tracking-wider text-black flex items-center gap-1.5">
                  <Quote className="h-3.5 w-3.5 text-[#FF0000]" />
                  VERBATIM FILING SNIPPET
                </span>
                <button
                  onClick={copySnippet}
                  className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase text-black border border-black bg-white hover:bg-black hover:text-white px-2.5 py-1 transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-black" />
                      <span>COPIED</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>COPY</span>
                    </>
                  )}
                </button>
              </div>

              <div className="border border-black bg-zinc-100 p-4 text-xs font-mono leading-relaxed text-black uppercase">
                &ldquo;{citation.snippet}&rdquo;
              </div>
            </div>

            {/* Ind AS & Audit Grounding Notice */}
            <div className="border border-black bg-white p-4 flex gap-3 shadow-[2px_2px_0px_#000000]">
              <ShieldCheck className="h-5 w-5 text-black shrink-0 mt-0.5" />
              <div className="text-xs font-mono uppercase space-y-1">
                <p className="font-bold text-black">AUDITABLE EVIDENCE GROUNDING</p>
                <p className="text-zinc-600 leading-relaxed text-[10px]">
                  FINDOC GROUNDINGS ARE DETERMINISTIC EXTRACTS TAGGED WITH DOCUMENT AND PAGE PROVENANCE. THE INFERENCE PROMPT IS ENFORCED WITH STRICT REFUSAL RULES TO ELIMINATE NUMERIC HALLUCINATIONS.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-black p-4 flex items-center justify-between bg-zinc-50">
          <p className="text-[10px] font-mono text-zinc-600 uppercase">PRESS ESC TO DISMISS</p>
          <Button
            size="sm"
            onClick={onClose}
            className="bg-black text-white hover:bg-black/90 rounded-none border border-black font-black uppercase text-xs px-4"
          >
            CLOSE
          </Button>
        </div>
      </div>
    </>
  );
}
