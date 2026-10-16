"use client";

import React from "react";
import { DocumentItem } from "@/types/document";
import { ArrowLeftRight, ChevronDown } from "lucide-react";
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
    <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-black pb-3">
        <div>
          <h3 className="text-xs font-black uppercase tracking-widest text-black flex items-center gap-2">
            <span className="text-[#FF0000]">[ 01 / SELECTION ]</span> COMPARATIVE PAIR CONFIGURATION
          </h3>
          <p className="text-[10px] font-mono text-zinc-600 uppercase mt-0.5">
            BENCHMARK BASELINE ENTITY AGAINST PEER OR HISTORICAL FILING
          </p>
        </div>
        <Button
          onClick={onCompare}
          disabled={!docAId || !docBId || docAId === docBId || isComparing}
          className="rounded-none border border-black bg-black text-white hover:bg-black/90 font-black uppercase tracking-wider text-xs px-5 py-2.5 shadow-[3px_3px_0px_#FF0000]"
        >
          {isComparing ? "CALCULATING DELTAS..." : "EXECUTE VARIANCE ANALYSIS"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
        {/* Document A (Baseline) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[10px] uppercase font-mono font-black tracking-wider text-black flex items-center gap-1.5">
            <span className="h-2 w-2 bg-black inline-block" />
            DOCUMENT A (BASELINE REFERENCE)
          </label>
          <div className="relative">
            <select
              value={docAId || ""}
              onChange={(e) => onSelectDocA(e.target.value)}
              className="w-full appearance-none rounded-none border border-black bg-white px-3.5 py-2.5 text-xs font-mono font-bold text-black shadow-[2px_2px_0px_#000000] focus:outline-none cursor-pointer"
            >
              <option value="" disabled className="bg-white">
                SELECT BASELINE FILING...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id} className="bg-white text-black font-mono">
                  {formatLabel(doc)} ({doc.filename})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-3 h-4 w-4 text-black" />
          </div>
        </div>

        {/* Swap Button */}
        <div className="md:col-span-1 flex justify-center pt-5 md:pt-4">
          <button
            type="button"
            onClick={onSwap}
            title="Swap Baseline and Target"
            className="flex h-9 w-9 items-center justify-center border border-black bg-white hover:bg-black hover:text-white text-black transition-colors shadow-[2px_2px_0px_#000000]"
          >
            <ArrowLeftRight className="h-4 w-4" />
          </button>
        </div>

        {/* Document B (Comparison) */}
        <div className="md:col-span-5 space-y-1.5">
          <label className="text-[10px] uppercase font-mono font-black tracking-wider text-black flex items-center gap-1.5">
            <span className="h-2 w-2 bg-[#FF0000] inline-block" />
            DOCUMENT B (TARGET / COMPARISON)
          </label>
          <div className="relative">
            <select
              value={docBId || ""}
              onChange={(e) => onSelectDocB(e.target.value)}
              className="w-full appearance-none rounded-none border border-black bg-white px-3.5 py-2.5 text-xs font-mono font-bold text-black shadow-[2px_2px_0px_#000000] focus:outline-none cursor-pointer"
            >
              <option value="" disabled className="bg-white">
                SELECT TARGET FILING...
              </option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id} className="bg-white text-black font-mono">
                  {formatLabel(doc)} ({doc.filename})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-3 h-4 w-4 text-black" />
          </div>
        </div>
      </div>
    </div>
  );
}
