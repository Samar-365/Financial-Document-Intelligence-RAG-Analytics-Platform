"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { FinancialMetricItem } from "@/types/financial";
import { Search, ChevronUp, ChevronDown, Database, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";

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

function SortIcon({ col, sortKey, sortDir }: { col: SortKey; sortKey: SortKey; sortDir: SortDir }) {
  if (col !== sortKey) return <ChevronUp className="h-3 w-3 text-zinc-400" />;
  return sortDir === "asc"
    ? <ChevronUp className="h-3 w-3 text-black" />
    : <ChevronDown className="h-3 w-3 text-black" />;
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
    { key: "metric_name", label: "METRIC LINE ITEM" },
    { key: "value", label: "VALUE", align: "text-right" },
    { key: "confidence", label: "CONFIDENCE", align: "text-center" },
    { key: "fiscal_year", label: "FY", align: "text-center" },
    { key: "source_page", label: "PAGE", align: "text-center" },
  ];

  if (isLoading) {
    return (
      <div className="space-y-2 p-4 border border-black bg-white">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 bg-zinc-200 animate-pulse" style={{ width: "35%" }} />
            <div className="h-4 w-20 bg-zinc-200 animate-pulse ml-auto" />
            <div className="h-4 w-12 bg-zinc-200 animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="border border-black bg-white shadow-[4px_4px_0px_#000000]">
      {/* Search bar */}
      <div className="flex items-center gap-3 border-b border-black p-3 bg-zinc-50">
        <Database className="h-4 w-4 text-black shrink-0" />
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="FILTER EXTRACTED LINE ITEMS..."
            className="pl-8 h-8 text-xs font-mono rounded-none border border-black bg-white text-black placeholder:text-zinc-400 focus-visible:ring-0 focus-visible:border-black shadow-[1px_1px_0px_#000000]"
          />
        </div>
        <span className="ml-auto text-[10px] font-mono text-zinc-500 uppercase">
          SHOWING {filtered.length} OF {metrics.length} ITEMS
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-black bg-black text-white">
              {COLS.map(({ key, label, align = "text-left" }) => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className={cn(
                    "py-2.5 px-3 text-[10px] font-mono font-black uppercase tracking-wider text-white cursor-pointer hover:bg-zinc-900 select-none",
                    align
                  )}
                >
                  <span className="inline-flex items-center gap-1">
                    {label}
                    <SortIcon col={key} sortKey={sortKey} sortDir={sortDir} />
                  </span>
                </th>
              ))}
              <th className="py-2.5 pr-3 text-right text-[10px] font-mono font-black uppercase text-white">
                TRACE
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-xs font-mono uppercase text-zinc-500">
                  NO METRICS MATCH SEARCH QUERY
                </td>
              </tr>
            ) : (
              filtered.map((m, idx) => {
                const confPct = Math.round((m.confidence ?? 0) * 100);
                return (
                  <tr
                    key={`${m.metric_name}-${idx}`}
                    onClick={() => onRowClick?.(m)}
                    className="border-b border-zinc-200 hover:bg-zinc-100 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-3 font-mono text-xs font-bold text-black">
                      {m.metric_name}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-xs font-black text-right text-black">
                      {formatValue(m, currencySymbol, unit)}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span
                        className={cn(
                          "inline-flex items-center px-1.5 py-0.5 text-[9px] font-mono font-black uppercase border border-black",
                          m.confidence >= 0.85
                            ? "bg-black text-white"
                            : m.confidence >= 0.6
                            ? "bg-zinc-200 text-black"
                            : "bg-[#FF0000] text-white"
                        )}
                      >
                        {confPct}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-xs text-center text-zinc-600">
                      {m.fiscal_year ? `FY${m.fiscal_year}` : "—"}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-xs text-center text-zinc-600">
                      {m.source_page ? `p.${m.source_page}` : "—"}
                    </td>
                    <td className="py-2.5 pr-3 text-right">
                      <ChevronRight className="ml-auto h-4 w-4 text-black hover:text-[#FF0000] transition-colors" />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
