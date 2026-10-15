"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { FinancialMetricItem } from "@/types/financial";
import {
  DollarSign,
  Layers,
  Activity,
  FileText,
  ChevronRight,
} from "lucide-react";

interface StatementTabsProps {
  metrics: FinancialMetricItem[];
  currencySymbol: string;
  unit: string;
  isLoading?: boolean;
  onChunkClick?: (metric: FinancialMetricItem) => void;
}

type StatementType = "pl" | "balance" | "cashflow";

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
        "group border-b border-zinc-200 transition-colors",
        hasValue ? "hover:bg-zinc-100 cursor-pointer" : "opacity-40"
      )}
      onClick={() => hasValue && metric && onChunkClick?.(metric)}
    >
      <td className={cn("py-3 pl-4 pr-2 font-mono text-xs", isSubItem ? "pl-8 text-zinc-600" : "text-black font-bold")}>
        {isSubItem && <span className="mr-1.5 text-zinc-400">└</span>}
        {label}
      </td>
      <td className="py-3 px-3 text-right font-mono text-xs font-black text-black">
        {valueStr}
      </td>
      <td className="py-3 px-3 text-center hidden sm:table-cell">
        {hasValue ? (
          <span
            className={cn(
              "inline-flex items-center px-2 py-0.5 text-[9px] font-mono font-black uppercase border border-black",
              conf >= 0.85
                ? "bg-black text-white"
                : conf >= 0.6
                ? "bg-zinc-200 text-black"
                : "bg-[#FF0000] text-white"
            )}
          >
            {confPct}% CONF
          </span>
        ) : (
          <span className="text-zinc-400 text-xs font-mono">—</span>
        )}
      </td>
      <td className="py-3 pr-4 text-center hidden md:table-cell font-mono text-xs text-zinc-600">
        {metric?.source_page ? `PAGE ${metric.source_page}` : "—"}
      </td>
      <td className="py-3 pr-4 text-right hidden lg:table-cell">
        {hasValue && onChunkClick && (
          <ChevronRight className="ml-auto h-4 w-4 text-black group-hover:text-[#FF0000] transition-colors" />
        )}
      </td>
    </tr>
  );
}

function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="space-y-2 p-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center justify-between">
          <div
            className="h-4 bg-zinc-200 animate-pulse"
            style={{ width: `${30 + (i % 4) * 15}%` }}
          />
          <div className="h-4 w-20 bg-zinc-200 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

const TABS: { id: StatementType; label: string; icon: React.ElementType }[] = [
  { id: "pl", label: "01. INCOME STATEMENT (P&L)", icon: DollarSign },
  { id: "balance", label: "02. BALANCE SHEET", icon: Layers },
  { id: "cashflow", label: "03. CASH FLOW STATEMENT", icon: Activity },
];

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
    <div className="border border-black bg-white shadow-[4px_4px_0px_#000000]">
      {/* Tab Bar */}
      <div className="flex border-b border-black bg-zinc-100 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            id={`tab-${id}`}
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex items-center gap-2 whitespace-nowrap px-6 py-3.5 text-xs font-mono font-black uppercase tracking-wider transition-all border-r border-black",
              activeTab === id
                ? "bg-black text-white"
                : "bg-white text-black hover:bg-zinc-50"
            )}
          >
            <Icon className={cn("h-3.5 w-3.5", activeTab === id ? "text-[#FF0000]" : "text-black")} />
            {label}
          </button>
        ))}
      </div>

      {/* Statement Table */}
      {isLoading ? (
        <TableSkeleton rows={10} />
      ) : metrics.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <FileText className="h-10 w-10 text-zinc-400" />
          <p className="text-xs font-mono uppercase text-zinc-500">
            NO LINE ITEMS EXTRACTED FOR ACTIVE FILING YET.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-black bg-black text-white">
                <th className="py-2.5 pl-4 text-left text-[10px] font-mono font-black uppercase tracking-widest text-white">
                  STANDARDIZED LINE ITEM
                </th>
                <th className="py-2.5 px-3 text-right text-[10px] font-mono font-black uppercase tracking-widest text-white">
                  REPORTED VALUE
                </th>
                <th className="py-2.5 px-3 text-center text-[10px] font-mono font-black uppercase tracking-widest text-white hidden sm:table-cell">
                  CONFIDENCE
                </th>
                <th className="py-2.5 pr-4 text-center text-[10px] font-mono font-black uppercase tracking-widest text-white hidden md:table-cell">
                  PROVENANCE PAGE
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
