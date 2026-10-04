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

interface SourceChunkDrawerProps {
  metric: FinancialMetricItem | null;
  onClose: () => void;
  currencySymbol: string;
  unit: string;
}

function confidenceColor(conf: number) {
  if (conf >= 0.85) return { text: "text-emerald-400", bg: "bg-emerald-500", label: "High" };
  if (conf >= 0.6) return { text: "text-amber-400", bg: "bg-amber-500", label: "Medium" };
  return { text: "text-red-400", bg: "bg-red-500", label: "Low" };
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
  const { text: confText, bg: confBg, label: confLabel } = confidenceColor(conf);

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
          "fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-300",
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
          "border-l border-slate-800/80 bg-slate-950/95 shadow-2xl backdrop-blur-xl",
          "flex flex-col transition-transform duration-300 ease-in-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 px-5 py-4">
          <div className="flex items-center gap-2.5">
            <FileSearch className="h-5 w-5 text-blue-400" />
            <div>
              <h3 className="text-sm font-bold text-white">Source Chunk Inspector</h3>
              <p className="text-xs text-slate-500">Extraction provenance & confidence</p>
            </div>
          </div>
          <button
            id="close-drawer-btn"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-700/60 bg-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        {metric ? (
          <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
            {/* Metric Name */}
            <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-4">
              <div className="flex items-start gap-2 mb-3">
                <Tag className="h-4 w-4 text-blue-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-0.5">
                    Metric Line Item
                  </p>
                  <p className="text-base font-bold text-white leading-tight">
                    {metric.metric_name}
                  </p>
                </div>
              </div>

              {/* Extracted value */}
              <div className="rounded-lg bg-blue-500/5 border border-blue-500/15 px-4 py-3 text-center">
                <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider font-semibold">
                  Extracted Value
                </p>
                <p className="text-2xl font-bold text-white">
                  {formatDisplayValue(metric, currencySymbol, unit)}
                </p>
                {metric.unit && (
                  <p className="text-xs text-slate-500 mt-0.5">Unit: {metric.unit}</p>
                )}
              </div>
            </div>

            {/* Metadata grid */}
            <div className="grid grid-cols-2 gap-3">
              {/* Confidence */}
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3 col-span-2">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <Percent className="h-3.5 w-3.5 text-slate-400" />
                    <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
                      Extraction Confidence
                    </span>
                  </div>
                  <span className={cn("text-sm font-bold", confText)}>
                    {Math.round(conf * 100)}% — {confLabel}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={cn("h-full rounded-full transition-all duration-700", confBg)}
                    style={{ width: `${Math.round(conf * 100)}%` }}
                  />
                </div>
                <p className="text-[10px] text-slate-600 mt-1.5 leading-relaxed">
                  {conf >= 0.85
                    ? "High confidence — extracted from clearly structured statement tables."
                    : conf >= 0.6
                    ? "Medium confidence — extracted with some ambiguity. Cross-check recommended."
                    : "Low confidence — may be inferred or extracted from unstructured text."}
                </p>
              </div>

              {/* Source Page */}
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
                    Source Page
                  </span>
                </div>
                <p className={cn("text-lg font-bold", metric.source_page ? "text-white" : "text-slate-600")}>
                  {metric.source_page ? `Page ${metric.source_page}` : "—"}
                </p>
              </div>

              {/* Fiscal Year */}
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
                    Fiscal Year
                  </span>
                </div>
                <p className={cn("text-lg font-bold", metric.fiscal_year ? "text-white" : "text-slate-600")}>
                  {metric.fiscal_year ? `FY${metric.fiscal_year}` : "—"}
                </p>
              </div>

              {/* Period */}
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Hash className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
                    Period
                  </span>
                </div>
                <p className={cn("text-sm font-semibold", metric.fiscal_period ? "text-white" : "text-slate-600")}>
                  {metric.fiscal_period ?? "—"}
                </p>
              </div>

              {/* Raw Unit */}
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Tag className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
                    Raw Unit
                  </span>
                </div>
                <p className="text-sm font-semibold text-white">
                  {metric.unit || "—"}
                </p>
              </div>
            </div>

            {/* Ind AS note */}
            <div className="rounded-xl border border-dashed border-indigo-500/20 bg-indigo-500/5 p-4">
              <p className="text-xs font-semibold text-indigo-400 mb-1">Ind AS Compliance Note</p>
              <p className="text-xs text-slate-500 leading-relaxed">
                This metric was extracted using LLM-assisted parsing against Ind AS / IFRS
                statement structures. Confidence scores reflect structured vs. unstructured
                extraction quality. Always verify against the source filing for audit purposes.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-sm text-slate-500">Select a metric row to inspect its source.</p>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-slate-800/80 px-5 py-3 flex items-center justify-between">
          <p className="text-xs text-slate-600">
            Click any statement row to inspect its extraction.
          </p>
          <button
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-white transition-colors"
          >
            Close esc
          </button>
        </div>
      </div>
    </>
  );
}
