"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { FinancialMetricItem } from "@/types/financial";
import {
  DollarSign,
  Layers,
  Activity,
  TrendingUp,
  FileText,
  ChevronRight,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface StatementTabsProps {
  metrics: FinancialMetricItem[];
  currencySymbol: string;
  unit: string;
  isLoading?: boolean;
  onChunkClick?: (metric: FinancialMetricItem) => void;
}

type StatementType = "pl" | "balance" | "cashflow";

// ── Statement category definitions ───────────────────────────────────────────

const PL_KEYWORDS = [
  { label: "Revenue / Net Sales", keys: ["revenue", "net sales", "turnover", "total income"] },
  { label: "Gross Profit", keys: ["gross profit", "gross margin"] },
  { label: "EBITDA", keys: ["ebitda"] },
  { label: "Operating Income (EBIT)", keys: ["operating income", "ebit", "operating profit"] },
  { label: "Finance Costs / Interest", keys: ["finance cost", "interest expense", "interest paid"] },
  { label: "Depreciation & Amortisation", keys: ["depreciation", "amortisation", "amortization"] },
  { label: "Profit Before Tax (PBT)", keys: ["profit before tax", "pbt", "earnings before tax"] },
  { label: "Tax Expense", keys: ["tax expense", "income tax", "current tax", "deferred tax"] },
  { label: "Net Income / PAT", keys: ["net income", "net profit", "profit after tax", "pat"] },
  { label: "Diluted EPS", keys: ["eps", "earnings per share", "diluted eps"] },
];

const BALANCE_KEYWORDS = [
  { label: "Total Assets", keys: ["total assets"] },
  { label: "Current Assets", keys: ["current assets"] },
  { label: "Non-Current Assets", keys: ["non-current assets", "fixed assets", "ppe"] },
  { label: "Cash & Equivalents", keys: ["cash", "cash equivalents", "cash & equivalents"] },
  { label: "Inventory", keys: ["inventory", "inventories", "stock"] },
  { label: "Trade Receivables", keys: ["trade receivables", "accounts receivable", "debtors"] },
  { label: "Total Liabilities", keys: ["total liabilities"] },
  { label: "Current Liabilities", keys: ["current liabilities"] },
  { label: "Total Debt / Borrowings", keys: ["total debt", "borrowings", "long term debt"] },
  { label: "Shareholders Equity", keys: ["equity", "shareholders equity", "net worth", "book value"] },
];

const CASHFLOW_KEYWORDS = [
  { label: "Operating Cash Flow (CFO)", keys: ["operating cash flow", "cash from operations", "cfo", "cash generated from operations"] },
  { label: "Capital Expenditure (CapEx)", keys: ["capex", "capital expenditure", "purchase of assets", "additions to ppe"] },
  { label: "Free Cash Flow", keys: ["free cash flow", "fcf"] },
  { label: "Investing Cash Flow (CFI)", keys: ["investing activities", "cfi", "cash used in investing"] },
  { label: "Financing Cash Flow (CFF)", keys: ["financing activities", "cff", "cash from financing"] },
  { label: "Net Change in Cash", keys: ["net change in cash", "net cash increase", "cash and cash equivalents at end"] },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function findMetricForRow(
  metrics: FinancialMetricItem[],
  keywords: string[]
): FinancialMetricItem | undefined {
  return metrics.find((m) =>
    keywords.some((kw) =>
      m.metric_name.toLowerCase().includes(kw.toLowerCase())
    )
  );
}

function formatValue(
  metric: FinancialMetricItem | undefined,
  currencySymbol: string,
  unit: string
): string {
  if (!metric || metric.value == null) return "—";
  const name = metric.metric_name.toLowerCase();
  if (name.includes("eps") || name.includes("per share")) {
    return `${currencySymbol}${metric.value.toFixed(2)}`;
  }
  if (name.includes("ratio") || name.includes("coverage")) {
    return `${metric.value.toFixed(2)}x`;
  }
  return `${currencySymbol}${metric.value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`;
}

function confidenceColor(conf: number): string {
  if (conf >= 0.85) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
  if (conf >= 0.6) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  return "text-red-400 bg-red-500/10 border-red-500/30";
}

// ── Statement Row ─────────────────────────────────────────────────────────────

function StatementRow({
  label,
  metric,
  currencySymbol,
  unit,
  isSubItem = false,
  onChunkClick,
}: {
  label: string;
  metric?: FinancialMetricItem;
  currencySymbol: string;
  unit: string;
  isSubItem?: boolean;
  onChunkClick?: (m: FinancialMetricItem) => void;
}) {
  const hasValue = metric && metric.value != null;
  const valueStr = formatValue(metric, currencySymbol, unit);
  const conf = metric?.confidence ?? 0;
  const confPct = Math.round(conf * 100);

  return (
    <tr
      className={cn(
        "group border-b border-slate-800/50 transition-colors",
        hasValue ? "hover:bg-slate-800/30 cursor-pointer" : "opacity-50"
      )}
      onClick={() => hasValue && metric && onChunkClick?.(metric)}
    >
      <td className={cn("py-2.5 pl-4 pr-2 text-sm", isSubItem ? "pl-8 text-slate-400" : "text-slate-200 font-medium")}>
        {isSubItem && <span className="mr-1.5 text-slate-600">└</span>}
        {label}
      </td>
      <td className="py-2.5 px-3 text-right text-sm font-semibold text-white">
        {valueStr}
      </td>
      <td className="py-2.5 px-3 text-center hidden sm:table-cell">
        {hasValue ? (
          <span
            className={cn(
              "inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-bold",
              confidenceColor(conf)
            )}
          >
            {confPct}%
          </span>
        ) : (
          <span className="text-slate-600 text-xs">—</span>
        )}
      </td>
      <td className="py-2.5 pr-4 text-center hidden md:table-cell">
        {metric?.source_page ? (
          <span className="text-xs text-slate-500">p.{metric.source_page}</span>
        ) : (
          <span className="text-slate-700 text-xs">—</span>
        )}
      </td>
      <td className="py-2.5 pr-4 text-right hidden lg:table-cell">
        {hasValue && onChunkClick && (
          <ChevronRight className="ml-auto h-4 w-4 text-slate-600 group-hover:text-blue-400 transition-colors" />
        )}
      </td>
    </tr>
  );
}

// ── Loading skeleton ──────────────────────────────────────────────────────────

function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="space-y-1 p-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center justify-between">
          <div
            className="h-4 rounded bg-slate-800 animate-pulse"
            style={{ width: `${30 + (i % 4) * 15}%` }}
          />
          <div className="h-4 w-20 rounded bg-slate-800 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

// ── Tab definitions ───────────────────────────────────────────────────────────

const TABS: { id: StatementType; label: string; icon: React.ElementType; color: string }[] = [
  { id: "pl", label: "Income Statement (P&L)", icon: DollarSign, color: "text-blue-400" },
  { id: "balance", label: "Balance Sheet", icon: Layers, color: "text-emerald-400" },
  { id: "cashflow", label: "Cash Flow", icon: Activity, color: "text-indigo-400" },
];

// ── Main Component ────────────────────────────────────────────────────────────

export function StatementTabs({
  metrics,
  currencySymbol,
  unit,
  isLoading = false,
  onChunkClick,
}: StatementTabsProps) {
  const [activeTab, setActiveTab] = useState<StatementType>("pl");

  const keywordMap: Record<StatementType, { label: string; keys: string[]; isSubItem?: boolean }[]> = {
    pl: PL_KEYWORDS,
    balance: BALANCE_KEYWORDS,
    cashflow: CASHFLOW_KEYWORDS,
  };

  const rows = keywordMap[activeTab];

  const SUB_ITEMS: string[] = [
    "Finance Costs / Interest",
    "Depreciation & Amortisation",
    "Tax Expense",
    "Diluted EPS",
    "Current Assets",
    "Non-Current Assets",
    "Cash & Equivalents",
    "Inventory",
    "Trade Receivables",
    "Current Liabilities",
    "Capital Expenditure (CapEx)",
    "Free Cash Flow",
  ];

  return (
    <div className="flex flex-col gap-0 rounded-xl border border-slate-800/80 overflow-hidden bg-slate-900/60 backdrop-blur-md">
      {/* Tab Bar */}
      <div className="flex border-b border-slate-800/80 bg-slate-950/40 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon, color }) => (
          <button
            key={id}
            id={`tab-${id}`}
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex items-center gap-2 whitespace-nowrap px-5 py-3.5 text-xs font-semibold transition-all border-b-2",
              activeTab === id
                ? `border-blue-500 text-white bg-slate-800/40 ${color}`
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
            )}
          >
            <Icon className={cn("h-3.5 w-3.5", activeTab === id ? color : "")} />
            {label}
          </button>
        ))}
      </div>

      {/* Statement Table */}
      {isLoading ? (
        <TableSkeleton rows={10} />
      ) : metrics.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <FileText className="h-10 w-10 text-slate-700" />
          <p className="text-sm text-slate-500">
            No metrics extracted for this filing yet.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800/60 bg-slate-950/30">
                <th className="py-2.5 pl-4 text-left text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Line Item
                </th>
                <th className="py-2.5 px-3 text-right text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                  Value
                </th>
                <th className="py-2.5 px-3 text-center text-[10px] font-semibold uppercase tracking-widest text-slate-500 hidden sm:table-cell">
                  Confidence
                </th>
                <th className="py-2.5 pr-4 text-center text-[10px] font-semibold uppercase tracking-widest text-slate-500 hidden md:table-cell">
                  Source Page
                </th>
                <th className="py-2.5 pr-4 hidden lg:table-cell" />
              </tr>
            </thead>
            <tbody>
              {rows.map(({ label, keys }) => {
                const metric = findMetricForRow(metrics, keys);
                return (
                  <StatementRow
                    key={label}
                    label={label}
                    metric={metric}
                    currencySymbol={currencySymbol}
                    unit={unit}
                    isSubItem={SUB_ITEMS.includes(label)}
                    onChunkClick={onChunkClick}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
