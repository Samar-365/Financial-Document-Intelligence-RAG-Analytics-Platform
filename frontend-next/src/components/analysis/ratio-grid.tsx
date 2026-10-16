"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { FinancialRatiosResponse } from "@/types/financial";
import {
  TrendingUp,
  ShieldCheck,
  Layers,
  RefreshCw,
  Info,
} from "lucide-react";

// ── Benchmarks ────────────────────────────────────────────────────────────────

interface RatioDef {
  key: keyof FinancialRatiosResponse;
  label: string;
  description: string;
  suffix: string;
  good: [number, number]; // [min, max] for "good" range
  warn: [number, number]; // warn range
  higherIsBetter: boolean;
  benchmark?: string;
}

const LIQUIDITY_RATIOS: RatioDef[] = [
  {
    key: "current_ratio",
    label: "Current Ratio",
    description: "Ability to cover short-term liabilities with short-term assets.",
    suffix: "x",
    good: [1.5, 3],
    warn: [1, 1.5],
    higherIsBetter: true,
    benchmark: "Ideal: 1.5x – 3.0x",
  },
  {
    key: "quick_ratio",
    label: "Quick Ratio",
    description: "Liquidity excluding inventory (acid-test).",
    suffix: "x",
    good: [1, 2.5],
    warn: [0.7, 1],
    higherIsBetter: true,
    benchmark: "Ideal: ≥ 1.0x",
  },
];

const PROFITABILITY_RATIOS: RatioDef[] = [
  {
    key: "opm",
    label: "Operating Margin (OPM)",
    description: "Operating profit as a % of revenue (pre-tax, pre-interest).",
    suffix: "%",
    good: [15, 100],
    warn: [8, 15],
    higherIsBetter: true,
    benchmark: "Healthy: > 15%",
  },
  {
    key: "npm",
    label: "Net Profit Margin (NPM)",
    description: "Net income as a % of revenue after all expenses and taxes.",
    suffix: "%",
    good: [10, 100],
    warn: [5, 10],
    higherIsBetter: true,
    benchmark: "Healthy: > 10%",
  },
  {
    key: "roe",
    label: "Return on Equity (ROE)",
    description: "Net income generated per unit of shareholder equity.",
    suffix: "%",
    good: [15, 100],
    warn: [8, 15],
    higherIsBetter: true,
    benchmark: "Healthy: > 15%",
  },
  {
    key: "roce",
    label: "Return on Capital Employed",
    description: "Pre-tax operating profit vs. total capital employed.",
    suffix: "%",
    good: [12, 100],
    warn: [6, 12],
    higherIsBetter: true,
    benchmark: "Healthy: > 12%",
  },
];

const SOLVENCY_RATIOS: RatioDef[] = [
  {
    key: "debt_to_equity",
    label: "Debt-to-Equity",
    description: "Total debt relative to shareholders equity.",
    suffix: "x",
    good: [0, 1],
    warn: [1, 2],
    higherIsBetter: false,
    benchmark: "Conservative: < 1.0x",
  },
  {
    key: "interest_coverage",
    label: "Interest Coverage",
    description: "EBIT multiples over interest expense — solvency cushion.",
    suffix: "x",
    good: [3, 100],
    warn: [1.5, 3],
    higherIsBetter: true,
    benchmark: "Safe: > 3.0x",
  },
];

type RatioCategory = {
  tag: string;
  label: string;
  icon: React.ElementType;
  ratios: RatioDef[];
};

const CATEGORIES: RatioCategory[] = [
  { tag: "01", label: "Liquidity Ratios", icon: ShieldCheck, ratios: LIQUIDITY_RATIOS },
  { tag: "02", label: "Profitability & Returns", icon: TrendingUp, ratios: PROFITABILITY_RATIOS },
  { tag: "03", label: "Solvency & Capital Structure", icon: Layers, ratios: SOLVENCY_RATIOS },
];

function getRatioStatus(
  value: number,
  def: RatioDef
): "good" | "warn" | "danger" {
  const [gMin, gMax] = def.good;
  const [wMin, wMax] = def.warn;

  if (value >= gMin && value <= gMax) return "good";
  if (value >= wMin && value <= wMax) return "warn";
  if (!def.higherIsBetter && value < def.good[0]) return "good";
  return "danger";
}

const STATUS_STYLES = {
  good: {
    bar: "bg-black",
    badge: "text-black bg-white border-black",
    label: "HEALTHY",
  },
  warn: {
    bar: "bg-zinc-800",
    badge: "text-black bg-zinc-200 border-black",
    label: "MONITOR",
  },
  danger: {
    bar: "bg-[#FF0000]",
    badge: "text-white bg-[#FF0000] border-black",
    label: "RISK",
  },
};

function RatioCard({ def, value }: { def: RatioDef; value: number | null | undefined }) {
  if (value == null) {
    return (
      <div className="border border-black bg-white p-5 flex flex-col gap-2 opacity-40 shadow-[2px_2px_0px_#000000]">
        <div className="flex items-start justify-between gap-2 border-b border-black pb-2">
          <span className="text-xs font-mono font-bold uppercase text-black">{def.label}</span>
          <span className="text-xs font-mono text-zinc-400">N/A</span>
        </div>
        <p className="text-[11px] font-mono text-zinc-500 leading-relaxed">{def.description}</p>
      </div>
    );
  }

  const status = getRatioStatus(value, def);
  const styles = STATUS_STYLES[status];

  let barPct: number;
  if (def.higherIsBetter) {
    const maxShow = def.good[1] < 100 ? def.good[1] * 1.5 : 40;
    barPct = Math.min((value / maxShow) * 100, 100);
  } else {
    const maxShow = def.warn[1] * 2;
    barPct = Math.min((value / maxShow) * 100, 100);
  }

  return (
    <div className="border border-black bg-white p-5 flex flex-col gap-3 shadow-[4px_4px_0px_#000000] hover:shadow-[6px_6px_0px_#000000] transition-shadow">
      <div className="flex items-start justify-between gap-2 border-b border-black pb-2">
        <span className="text-xs font-black uppercase tracking-wider text-black">{def.label}</span>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xl font-black text-black">
            {value.toFixed(2)}{def.suffix}
          </span>
          <span
            className={cn(
              "border px-1.5 py-0.5 text-[9px] font-mono font-black uppercase tracking-wider",
              styles.badge
            )}
          >
            {styles.label}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-2 w-full border border-black bg-zinc-100 p-0.5">
        <div
          className={cn("h-full transition-all duration-500", styles.bar)}
          style={{ width: `${barPct}%` }}
        />
      </div>

      <div className="flex items-center justify-between gap-2 text-xs font-mono">
        <p className="text-zinc-600 text-[11px] leading-relaxed flex-1">{def.description}</p>
        {def.benchmark && (
          <span className="text-[10px] font-bold text-black border border-black bg-zinc-100 px-1.5 py-0.5 uppercase shrink-0">
            {def.benchmark}
          </span>
        )}
      </div>
    </div>
  );
}

function RatioSkeleton({ count }: { count: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="border border-black bg-white p-5 space-y-3 shadow-[3px_3px_0px_#000000]">
          <div className="flex justify-between">
            <div className="h-4 w-28 bg-zinc-200 animate-pulse" />
            <div className="h-4 w-16 bg-zinc-200 animate-pulse" />
          </div>
          <div className="h-2 w-full bg-zinc-200 animate-pulse" />
          <div className="h-3 w-40 bg-zinc-200 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

interface RatioGridProps {
  ratios: FinancialRatiosResponse | null | undefined;
  isLoading?: boolean;
}

export function RatioGrid({ ratios, isLoading = false }: RatioGridProps) {
  return (
    <div className="flex flex-col gap-8">
      {CATEGORIES.map(({ tag, label, ratios: defs }) => (
        <div key={label}>
          <div className="flex items-center justify-between border-b border-black pb-2 mb-4">
            <h4 className="text-xs font-black uppercase tracking-widest text-black flex items-center gap-2">
              <span className="text-[#FF0000]">[ {tag} ]</span> {label}
            </h4>
            <span className="text-[10px] font-mono text-zinc-500 uppercase">STANDARDIZED FORMULAS</span>
          </div>
          {isLoading ? (
            <RatioSkeleton count={defs.length} />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {defs.map((def) => (
                <RatioCard
                  key={def.key}
                  def={def}
                  value={ratios?.[def.key] as number | null | undefined}
                />
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Turnover stub */}
      <div>
        <div className="flex items-center justify-between border-b border-black pb-2 mb-4">
          <h4 className="text-xs font-black uppercase tracking-widest text-black flex items-center gap-2">
            <span className="text-[#FF0000]">[ 04 ]</span> TURNOVER &amp; EFFICIENCY RATIOS
          </h4>
          <span className="text-[10px] font-mono text-zinc-500 uppercase">PROJECTION</span>
        </div>
        <div className="border border-black bg-white p-5 flex items-center gap-4 shadow-[3px_3px_0px_#000000]">
          <RefreshCw className="h-5 w-5 text-black shrink-0" />
          <p className="text-xs font-mono uppercase text-zinc-700 leading-relaxed">
            Asset Turnover, Receivables Turnover, and Inventory Days metrics will automatically populate once multi-period statement data is ingested.
          </p>
        </div>
      </div>
    </div>
  );
}
