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
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md space-y-4">
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
          className="font-semibold shadow-md shadow-blue-500/20"
        >
          {isComparing ? "Analyzing..." : "Run Comparative Delta"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-11 gap-3 items-center">
        {/* Document A (Baseline) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[11px] uppercase tracking-wider font-bold text-blue-400 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-blue-500 inline-block" />
            Document A (Baseline Reference)
          </label>
          <div className="relative">
            <select
              value={docAId || ""}
              onChange={(e) => onSelectDocA(e.target.value)}
              className="w-full appearance-none rounded-xl border border-slate-800 bg-slate-950 px-3.5 py-2.5 text-xs font-medium text-white shadow-inner focus:border-blue-500 focus:outline-none"
            >
              <option value="" disabled>
                Select baseline filing...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
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
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-800 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-all shadow-md hover:scale-105"
          >
            <ArrowLeftRight className="h-4 w-4" />
          </button>
        </div>

        {/* Document B (Comparison) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[11px] uppercase tracking-wider font-bold text-indigo-400 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-indigo-500 inline-block" />
            Document B (Target / Comparison)
          </label>
          <div className="relative">
            <select
              value={docBId || ""}
              onChange={(e) => onSelectDocB(e.target.value)}
              className="w-full appearance-none rounded-xl border border-slate-800 bg-slate-950 px-3.5 py-2.5 text-xs font-medium text-white shadow-inner focus:border-indigo-500 focus:outline-none"
            >
              <option value="" disabled>
                Select target filing...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
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
