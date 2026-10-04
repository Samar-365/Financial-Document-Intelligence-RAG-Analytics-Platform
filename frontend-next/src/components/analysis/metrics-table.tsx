"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { FinancialMetricItem } from "@/types/financial";
import { Search, ChevronUp, ChevronDown, Database, FileSearch } from "lucide-react";

interface MetricsTableProps {
  metrics: FinancialMetricItem[];
  currencySymbol: string;
  unit: string;
  isLoading?: boolean;
  onRowClick?: (metric: FinancialMetricItem) => void;
}

type SortKey = "metric_name" | "value" | "confidence" | "fiscal_year" | "source_page";
type SortDir = "asc" | "desc";

function formatValue(m: FinancialMetricItem, sym: string, unit: string): string {
  if (m.value == null) return "—";
  const name = m.metric_name.toLowerCase();
  if (name.includes("eps") || name.includes("per share")) {
    return `${sym}${m.value.toFixed(2)}`;
  }
  return `${sym}${m.value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`;
}

function confidenceBadge(conf: number) {
  if (conf >= 0.85) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
  if (conf >= 0.6) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  return "text-red-400 bg-red-500/10 border-red-500/30";
}

function SortIcon({ col, sortKey, sortDir }: { col: SortKey; sortKey: SortKey; sortDir: SortDir }) {
  if (col !== sortKey) return <ChevronUp className="h-3 w-3 text-slate-700" />;
  return sortDir === "asc"
    ? <ChevronUp className="h-3 w-3 text-blue-400" />
    : <ChevronDown className="h-3 w-3 text-blue-400" />;
}

export function MetricsTable({
  metrics,
  currencySymbol,
  unit,
  isLoading = false,
  onRowClick,
}: MetricsTableProps) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("metric_name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  };

  const filtered = metrics
    .filter((m) =>
      m.metric_name.toLowerCase().includes(search.toLowerCase()) ||
      (m.unit ?? "").toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      let av: string | number = 0;
      let bv: string | number = 0;
      if (sortKey === "metric_name") { av = a.metric_name; bv = b.metric_name; }
      else if (sortKey === "value") { av = a.value ?? -Infinity; bv = b.value ?? -Infinity; }
      else if (sortKey === "confidence") { av = a.confidence; bv = b.confidence; }
      else if (sortKey === "fiscal_year") { av = a.fiscal_year ?? 0; bv = b.fiscal_year ?? 0; }
      else if (sortKey === "source_page") { av = a.source_page ?? 0; bv = b.source_page ?? 0; }
      if (typeof av === "string") return sortDir === "asc" ? av.localeCompare(String(bv)) : String(bv).localeCompare(av);
      return sortDir === "asc" ? (av as number) - (bv as number) : (bv as number) - (av as number);
    });

  const COLS: { key: SortKey; label: string; align?: string }[] = [
    { key: "metric_name", label: "Metric Line Item" },
    { key: "value", label: "Value", align: "text-right" },
    { key: "confidence", label: "Confidence", align: "text-center" },
    { key: "fiscal_year", label: "FY", align: "text-center" },
    { key: "source_page", label: "Page", align: "text-center" },
  ];

  if (isLoading) {
    return (
      <div className="space-y-1.5 p-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 rounded bg-slate-800 animate-pulse" style={{ width: "35%" }} />
            <div className="h-4 w-20 rounded bg-slate-800 animate-pulse ml-auto" />
            <div className="h-4 w-12 rounded bg-slate-800 animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-0 rounded-xl border border-slate-800/80 overflow-hidden bg-slate-900/60 backdrop-blur-md">
      {/* Search bar */}
      <div className="flex items-center gap-3 border-b border-slate-800/80 px-4 py-3 bg-slate-950/30">
        <Database className="h-4 w-4 text-slate-500 shrink-0" />
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">
          All Extracted Metrics
        </span>
        <span className="ml-auto text-xs text-slate-500">{filtered.length} items</span>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
          <input
            id="metrics-search"
            type="text"
            placeholder="Search metrics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 w-48 rounded-lg border border-slate-700/60 bg-slate-800/60 pl-8 pr-3 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500/60 transition-colors"
          />
        </div>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 gap-2">
          <FileSearch className="h-8 w-8 text-slate-700" />
          <p className="text-sm text-slate-500">
            {search ? `No metrics matching "${search}"` : "No metrics extracted yet."}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800/60 bg-slate-950/30">
                {COLS.map(({ key, label, align }) => (
                  <th
                    key={key}
                    className={cn(
                      "py-2.5 px-4 text-[10px] font-semibold uppercase tracking-widest text-slate-500 cursor-pointer select-none hover:text-slate-300 transition-colors",
                      align ?? "text-left"
                    )}
                    onClick={() => handleSort(key)}
                  >
                    <span className="inline-flex items-center gap-1">
                      {label}
                      <SortIcon col={key} sortKey={sortKey} sortDir={sortDir} />
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((m, idx) => (
                <tr
                  key={`${m.metric_name}-${idx}`}
                  className="group border-b border-slate-800/40 hover:bg-slate-800/30 cursor-pointer transition-colors"
                  onClick={() => onRowClick?.(m)}
                >
                  <td className="py-2.5 pl-4 pr-3 text-sm text-slate-200 font-medium">
                    {m.metric_name}
                  </td>
                  <td className="py-2.5 px-4 text-right text-sm font-semibold text-white">
                    {formatValue(m, currencySymbol, unit)}
                  </td>
                  <td className="py-2.5 px-4 text-center">
                    <span
                      className={cn(
                        "inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-bold",
                        confidenceBadge(m.confidence)
                      )}
                    >
                      {Math.round(m.confidence * 100)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-center text-xs text-slate-400">
                    {m.fiscal_year ? `FY${m.fiscal_year}` : "—"}
                  </td>
                  <td className="py-2.5 px-4 text-center text-xs text-slate-500">
                    {m.source_page ? `p.${m.source_page}` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
