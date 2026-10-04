"use client";

import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { FinancialMetricItem } from "@/types/financial";

interface CapitalDonutChartProps {
  metrics: FinancialMetricItem[];
  currencySymbol: string;
  unit: string;
  isLoading?: boolean;
}

const COLORS = {
  equity: "#10b981",   // emerald
  debt: "#ef4444",     // red
  cash: "#3b82f6",     // blue
  other: "#6366f1",    // indigo
};

const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { name: string; value: number; payload: { color: string } }[];
}) => {
  if (active && payload && payload.length) {
    const entry = payload[0];
    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 px-3 py-2 text-xs shadow-2xl">
        <p className="font-semibold mb-0.5" style={{ color: entry.payload.color }}>
          {entry.name}
        </p>
        <p className="text-white font-bold">
          {entry.value?.toLocaleString(undefined, { maximumFractionDigits: 1 })}
        </p>
      </div>
    );
  }
  return null;
};



export function CapitalDonutChart({
  metrics,
  currencySymbol,
  unit,
  isLoading = false,
}: CapitalDonutChartProps) {
  // Extract capital structure metrics
  let equity: number | null = null;
  let debt: number | null = null;
  let cash: number | null = null;

  for (const m of metrics) {
    const name = m.metric_name.toLowerCase();
    if (name.includes("equity") || name.includes("shareholders")) {
      equity = m.value ?? null;
    } else if (
      name.includes("total debt") ||
      name.includes("borrowings") ||
      name.includes("long term debt")
    ) {
      debt = m.value ?? null;
    } else if (name.includes("cash") || name.includes("cash equivalent")) {
      cash = m.value ?? null;
    }
  }

  const segments: { name: string; value: number; color: string }[] = [];
  if (equity !== null && equity > 0)
    segments.push({ name: "Equity", value: equity, color: COLORS.equity });
  if (debt !== null && debt > 0)
    segments.push({ name: "Debt", value: debt, color: COLORS.debt });
  if (cash !== null && cash > 0)
    segments.push({ name: "Cash", value: cash, color: COLORS.cash });

  // If no data, show placeholder
  const displayData =
    segments.length > 0
      ? segments
      : [
          { name: "Equity", value: 60, color: COLORS.equity },
          { name: "Debt", value: 30, color: COLORS.debt },
          { name: "Cash", value: 10, color: COLORS.cash },
        ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-44 w-44 rounded-full border-[18px] border-slate-800 animate-pulse" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <defs>
          {displayData.map((d) => (
            <filter key={d.name} id={`glow-${d.name}`}>
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          ))}
        </defs>
        <Pie
          data={displayData}
          cx="50%"
          cy="50%"
          innerRadius="52%"
          outerRadius="75%"
          paddingAngle={3}
          dataKey="value"
          labelLine={false}
        >
          {displayData.map((entry) => (
            <Cell
              key={entry.name}
              fill={entry.color}
              stroke={entry.color}
              strokeWidth={0}
              style={{ filter: `drop-shadow(0 0 6px ${entry.color}55)` }}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          formatter={(value) => (
            <span className="text-xs text-slate-400">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
