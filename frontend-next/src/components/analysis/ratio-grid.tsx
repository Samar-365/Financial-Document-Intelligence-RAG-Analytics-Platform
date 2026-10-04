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
    label: "Operating Margin",
    description: "Operating profit as a % of revenue (pre-tax, pre-interest).",
    suffix: "%",
    good: [15, 100],
    warn: [8, 15],
    higherIsBetter: true,
    benchmark: "Healthy: > 15%",
  },
  {
    key: "npm",
    label: "Net Profit Margin",
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
  label: string;
  icon: React.ElementType;
  color: string;
  ratios: RatioDef[];
};

const CATEGORIES: RatioCategory[] = [
  { label: "Liquidity", icon: ShieldCheck, color: "text-cyan-400", ratios: LIQUIDITY_RATIOS },
  { label: "Profitability", icon: TrendingUp, color: "text-emerald-400", ratios: PROFITABILITY_RATIOS },
  { label: "Solvency & Leverage", icon: Layers, color: "text-amber-400", ratios: SOLVENCY_RATIOS },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

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
    bar: "bg-emerald-500",
    badge: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    label: "Healthy",
  },
  warn: {
    bar: "bg-amber-500",
    badge: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    label: "Monitor",
  },
  danger: {
    bar: "bg-red-500",
    badge: "text-red-400 bg-red-500/10 border-red-500/30",
    label: "At Risk",
  },
};

// ── Ratio Card ────────────────────────────────────────────────────────────────

function RatioCard({ def, value }: { def: RatioDef; value: number | null | undefined }) {
  if (value == null) {
    return (
      <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-4 flex flex-col gap-2 opacity-40">
        <div className="flex items-start justify-between gap-2">
          <span className="text-xs font-semibold text-slate-300">{def.label}</span>
          <span className="text-xs text-slate-600">N/A</span>
        </div>
        <div className="h-1 w-full rounded-full bg-slate-800" />
        <p className="text-[11px] text-slate-600 leading-relaxed">{def.description}</p>
      </div>
    );
  }

  const status = getRatioStatus(value, def);
  const styles = STATUS_STYLES[status];

  // Bar fill: clamp to 0-100%
  let barPct: number;
  if (def.higherIsBetter) {
    const maxShow = def.good[1] < 100 ? def.good[1] * 1.5 : 40;
    barPct = Math.min((value / maxShow) * 100, 100);
  } else {
    const maxShow = def.warn[1] * 2;
    barPct = Math.min((value / maxShow) * 100, 100);
  }

  return (
    <div className="group rounded-xl border border-slate-800/60 bg-slate-900/40 p-4 flex flex-col gap-2 hover:border-slate-700/80 transition-all">
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold text-slate-200 leading-tight">{def.label}</span>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-base font-bold text-white">
            {value.toFixed(2)}{def.suffix}
          </span>
          <span
            className={cn(
              "rounded border px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider",
              styles.badge
            )}
          >
            {styles.label}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-700", styles.bar)}
          style={{ width: `${barPct}%` }}
        />
      </div>

      <div className="flex items-center justify-between gap-2">
        <p className="text-[11px] text-slate-500 leading-relaxed flex-1">{def.description}</p>
        {def.benchmark && (
          <span className="text-[10px] text-slate-600 shrink-0 flex items-center gap-0.5">
            <Info className="h-2.5 w-2.5" />
            {def.benchmark}
          </span>
        )}
      </div>
    </div>
  );
}

// ── Loading skeleton ──────────────────────────────────────────────────────────

function RatioSkeleton({ count }: { count: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-4 space-y-2">
          <div className="flex justify-between">
            <div className="h-3.5 w-28 rounded bg-slate-800 animate-pulse" />
            <div className="h-3.5 w-16 rounded bg-slate-800 animate-pulse" />
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-800 animate-pulse" />
          <div className="h-3 w-40 rounded bg-slate-800/60 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface RatioGridProps {
  ratios: FinancialRatiosResponse | null | undefined;
  isLoading?: boolean;
}

export function RatioGrid({ ratios, isLoading = false }: RatioGridProps) {
  return (
    <div className="flex flex-col gap-6">
      {CATEGORIES.map(({ label, icon: Icon, color, ratios: defs }) => (
        <div key={label}>
          <div className="flex items-center gap-2 mb-3">
            <Icon className={cn("h-4 w-4", color)} />
            <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              {label} Ratios
            </h4>
          </div>
          {isLoading ? (
            <RatioSkeleton count={defs.length} />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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

      {/* Turnover stub — no backend endpoint yet */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <RefreshCw className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Turnover Ratios
          </h4>
        </div>
        <div className="rounded-xl border border-dashed border-slate-700/40 bg-slate-900/20 p-5 flex items-center gap-3">
          <RefreshCw className="h-5 w-5 text-slate-600 shrink-0" />
          <p className="text-xs text-slate-500 leading-relaxed">
            Asset Turnover, Receivables Turnover, and Inventory Turnover ratios will be
            available once the backend exposes turnover endpoints.
          </p>
        </div>
      </div>
    </div>
  );
}
