"use client";

import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { FinancialMetricItem } from "@/types/financial";
import {
  X,
  FileSearch,
  BookOpen,
  Percent,
  Hash,
  Calendar,
  Tag,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface SourceChunkDrawerProps {
  metric: FinancialMetricItem | null;
  onClose: () => void;
  currencySymbol: string;
  unit: string;
}

function formatDisplayValue(m: FinancialMetricItem, sym: string, unit: string): string {
  if (m.value == null) return "—";
  const name = m.metric_name.toLowerCase();
  if (name.includes("eps") || name.includes("per share")) {
    return `${sym}${m.value.toFixed(2)}`;
  }
  if (name.includes("ratio") || name.includes("coverage")) {
    return `${m.value.toFixed(2)}x`;
  }
  return `${sym}${m.value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`;
}

export function SourceChunkDrawer({
  metric,
  onClose,
  currencySymbol,
  unit,
}: SourceChunkDrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);
  const isOpen = !!metric;
  const conf = metric?.confidence ?? 0;
  const confPct = Math.round(conf * 100);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Prevent scroll on body while open
  useEffect(() => {
    if (isOpen) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

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

      {/* Drawer panel */}
      <div
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-label="Source Chunk Inspector"
        className={cn(
          "fixed right-0 top-0 z-50 h-full w-full max-w-md",
          "border-l-2 border-black bg-white shadow-[-8px_0px_0px_#000000]",
          "flex flex-col transition-transform duration-200 ease-in-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-black p-5 bg-white">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center border border-black bg-black text-white shrink-0">
              <FileSearch className="h-4 w-4 text-[#FF0000]" />
            </div>
            <div>
              <h3 className="text-xs font-black uppercase tracking-wider text-black">
                SOURCE CHUNK INSPECTOR
              </h3>
              <p className="text-[10px] font-mono text-zinc-600 uppercase">PROVENANCE &amp; CONFIDENCE TRACE</p>
            </div>
          </div>
          <button
            id="close-drawer-btn"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center border border-black bg-white text-black hover:bg-black hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        {metric ? (
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Metric Name */}
            <div className="border border-black bg-white p-5 shadow-[4px_4px_0px_#000000]">
              <div className="flex items-start gap-2 mb-3 border-b border-black pb-2">
                <Tag className="h-4 w-4 text-black mt-0.5 shrink-0" />
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase font-mono tracking-widest">
                    METRIC LINE ITEM
                  </p>
                  <p className="text-base font-black text-black uppercase leading-tight">
                    {metric.metric_name}
                  </p>
                </div>
              </div>

              {/* Extracted value */}
              <div className="border border-black bg-zinc-100 p-4 text-center">
                <p className="text-[10px] text-black uppercase tracking-wider font-mono font-bold mb-1">
                  EXTRACTED VALUE
                </p>
                <p className="text-3xl font-black text-black">
                  {formatDisplayValue(metric, currencySymbol, unit)}
                </p>
                {metric.unit && (
                  <p className="text-[10px] font-mono text-zinc-600 mt-1 uppercase">REPORTED UNIT: {metric.unit}</p>
                )}
              </div>
            </div>

            {/* Metadata grid */}
            <div className="grid grid-cols-2 gap-3">
              {/* Confidence */}
              <div className="border border-black bg-white p-4 col-span-2 shadow-[2px_2px_0px_#000000]">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <Percent className="h-3.5 w-3.5 text-black" />
                    <span className="text-[10px] uppercase tracking-widest font-mono font-bold text-black">
                      EXTRACTION CONFIDENCE
                    </span>
                  </div>
                  <span className="text-xs font-mono font-black uppercase text-black">
                    {confPct}%
                  </span>
                </div>
                <div className="h-2 w-full border border-black bg-zinc-100 p-0.5">
                  <div
                    className={cn(
                      "h-full transition-all duration-500",
                      conf >= 0.85 ? "bg-black" : conf >= 0.6 ? "bg-zinc-700" : "bg-[#FF0000]"
                    )}
                    style={{ width: `${confPct}%` }}
                  />
                </div>
                <p className="text-[10px] font-mono text-zinc-600 mt-2 leading-relaxed uppercase">
                  {conf >= 0.85
                    ? "HIGH CONFIDENCE — EXTRACTED FROM STANDARDIZED GAAP / IFRS FINANCIAL STATEMENTS."
                    : conf >= 0.6
                    ? "MEDIUM CONFIDENCE — EXTRACTED WITH POTENTIAL FOOTNOTE DEPENDENCY."
                    : "LOW CONFIDENCE — INFERRED FROM UNSTRUCTURED DISCLOSURE PARAGRAPH."}
                </p>
              </div>

              {/* Source Page */}
              <div className="border border-black bg-white p-3 shadow-[2px_2px_0px_#000000]">
                <div className="flex items-center gap-1.5 mb-1">
                  <BookOpen className="h-3.5 w-3.5 text-black" />
                  <span className="text-[10px] uppercase tracking-widest font-mono text-zinc-600">
                    PAGE
                  </span>
                </div>
                <p className="text-base font-black text-black font-mono">
                  {metric.source_page ? `PAGE ${metric.source_page}` : "—"}
                </p>
              </div>

              {/* Fiscal Year */}
              <div className="border border-black bg-white p-3 shadow-[2px_2px_0px_#000000]">
                <div className="flex items-center gap-1.5 mb-1">
                  <Calendar className="h-3.5 w-3.5 text-black" />
                  <span className="text-[10px] uppercase tracking-widest font-mono text-zinc-600">
                    YEAR
                  </span>
                </div>
                <p className="text-base font-black text-black font-mono">
                  {metric.fiscal_year ? `FY${metric.fiscal_year}` : "—"}
                </p>
              </div>

              {/* Period */}
              <div className="border border-black bg-white p-3 shadow-[2px_2px_0px_#000000]">
                <div className="flex items-center gap-1.5 mb-1">
                  <Hash className="h-3.5 w-3.5 text-black" />
                  <span className="text-[10px] uppercase tracking-widest font-mono text-zinc-600">
                    PERIOD
                  </span>
                </div>
                <p className="text-xs font-bold text-black font-mono uppercase">
                  {metric.fiscal_period ?? "—"}
                </p>
              </div>

              {/* Raw Unit */}
              <div className="border border-black bg-white p-3 shadow-[2px_2px_0px_#000000]">
                <div className="flex items-center gap-1.5 mb-1">
                  <Tag className="h-3.5 w-3.5 text-black" />
                  <span className="text-[10px] uppercase tracking-widest font-mono text-zinc-600">
                    SCALE
                  </span>
                </div>
                <p className="text-xs font-bold text-black font-mono uppercase">
                  {metric.unit || "—"}
                </p>
              </div>
            </div>

            {/* Ind AS note */}
            <div className="border border-black bg-white p-4 shadow-[2px_2px_0px_#000000]">
              <p className="text-xs font-black uppercase text-black mb-1">AUDIT VERIFICATION NOTE</p>
              <p className="text-[10px] font-mono text-zinc-700 leading-relaxed uppercase">
                THIS METRIC WAS PARSED VIA DEEP MULTI-PASS VECTOR CHUNKING AGAINST Ind AS / US-GAAP SCHEDULES. CONFIDENCE IS COMPUTED FROM SPATIAL PROXIMITY AND STATEMENT LINE CONTEXT.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-6 text-center">
            <p className="text-xs font-mono uppercase text-zinc-500">SELECT A STATEMENT ROW TO VIEW ITS PROVENANCE CHUNK.</p>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-black p-4 flex items-center justify-between bg-zinc-50">
          <p className="text-[10px] font-mono text-zinc-600 uppercase">
            CLICK ROW IN STATEMENT TABLE TO INSPECT
          </p>
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
