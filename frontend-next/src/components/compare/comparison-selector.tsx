"use client";

import React from "react";
import { DocumentItem } from "@/types/document";
import { ArrowLeftRight, Check, ChevronDown, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ComparisonSelectorProps {
  documents: DocumentItem[];
  docAId: string | null;
  docBId: string | null;
  onSelectDocA: (id: string) => void;
  onSelectDocB: (id: string) => void;
  onSwap: () => void;
  onCompare: () => void;
  isComparing: boolean;
}

export function ComparisonSelector({
  documents,
  docAId,
  docBId,
  onSelectDocA,
  onSelectDocB,
  onSwap,
  onCompare,
  isComparing,
}: ComparisonSelectorProps) {
  const formatLabel = (doc: DocumentItem) => {
    const name = doc.company_name || doc.filename;
    const period = doc.fiscal_period ? `${doc.fiscal_period} ` : "";
    const year = doc.fiscal_year ? `FY${doc.fiscal_year}` : "";
    return `${name} • ${period}${year}`.trim();
  };

  return (
    <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-5 shadow-xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-white">Select Comparison Pair</h3>
          <p className="text-xs text-slate-400">
            Compare baseline entity against a target fiscal year or peer competitor
          </p>
        </div>
        <Button
          onClick={onCompare}
          disabled={!docAId || !docBId || docAId === docBId || isComparing}
          variant="gradient"
          size="sm"
          className="font-semibold"
        >
          {isComparing ? "Analyzing..." : "Run Comparative Delta"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-11 gap-3 items-center">
        {/* Document A (Baseline) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[11px] uppercase tracking-wider font-bold text-[#E63946] flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#E63946] inline-block shadow-[0_0_8px_#E63946]" />
            Document A (Baseline Reference)
          </label>
          <div className="relative">
            <select
              value={docAId || ""}
              onChange={(e) => onSelectDocA(e.target.value)}
              className="w-full appearance-none rounded-xl border border-[rgba(184,29,36,0.35)] bg-[#14131D] px-3.5 py-2.5 text-xs font-medium text-white shadow-inner focus:border-[#E63946] focus:outline-none"
            >
              <option value="" disabled className="bg-[#14131D]">
                Select baseline filing...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id} className="bg-[#14131D]">
                  {formatLabel(doc)} ({doc.filename})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-3 h-4 w-4 text-slate-400" />
          </div>
        </div>

        {/* Swap Button */}
        <div className="md:col-span-1 flex justify-center pt-5 md:pt-4">
          <button
            type="button"
            onClick={onSwap}
            title="Swap Baseline and Target"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-[rgba(196,30,58,0.3)] bg-[#14131D] hover:bg-[rgba(184,29,36,0.2)] text-slate-300 hover:text-white hover:border-[#E63946] transition-all shadow-md hover:scale-105"
          >
            <ArrowLeftRight className="h-4 w-4" />
          </button>
        </div>

        {/* Document B (Comparison) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[11px] uppercase tracking-wider font-bold text-[#FF4D6D] flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#FF4D6D] inline-block shadow-[0_0_8px_#FF4D6D]" />
            Document B (Target / Comparison)
          </label>
          <div className="relative">
            <select
              value={docBId || ""}
              onChange={(e) => onSelectDocB(e.target.value)}
              className="w-full appearance-none rounded-xl border border-[rgba(184,29,36,0.35)] bg-[#14131D] px-3.5 py-2.5 text-xs font-medium text-white shadow-inner focus:border-[#E63946] focus:outline-none"
            >
              <option value="" disabled className="bg-[#14131D]">
                Select target filing...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id} className="bg-[#14131D]">
                  {formatLabel(doc)} ({doc.filename})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-3 h-4 w-4 text-slate-400" />
          </div>
        </div>
      </div>

      {docAId && docBId && docAId === docBId && (
        <p className="text-xs text-amber-400 font-medium">
          ⚠️ Please select two different documents to perform comparative delta calculations.
        </p>
      )}
    </div>
  );
}
