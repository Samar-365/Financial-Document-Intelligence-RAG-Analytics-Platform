"use client";

import React from "react";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { FinancialMetricItem } from "@/types/financial";

interface RevenueTrendChartProps {
  metrics: FinancialMetricItem[];
  currencySymbol: string;
  unit: string;
  isLoading?: boolean;
}

const CustomTooltip = ({
  active,
  payload,
  label,
  currencySymbol,
  unit,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
  currencySymbol?: string;
  unit?: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 px-4 py-3 text-xs shadow-2xl">
        <p className="font-semibold text-white mb-2 text-sm">{label}</p>
        {payload.map((entry) => (
          <div key={entry.name} className="flex items-center gap-2 mb-1">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ background: entry.color }}
            />
            <span className="text-slate-400">{entry.name}:</span>
            <span className="font-bold text-white">
              {currencySymbol}
              {entry.value?.toLocaleString(undefined, { maximumFractionDigits: 1 })} {unit}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function RevenueTrendChart({
  metrics,
  currencySymbol,
  unit,
  isLoading = false,
}: RevenueTrendChartProps) {
  // Build chart data from metrics grouped by fiscal year
  const byYear: Record<
    string,
    { year: string; revenue?: number; netIncome?: number; ebitda?: number }
  > = {};

  for (const m of metrics) {
    const yr = m.fiscal_year ? `FY${m.fiscal_year}` : "Current";
    if (!byYear[yr]) byYear[yr] = { year: yr };

    const name = m.metric_name.toLowerCase();
    if (name.includes("revenue") || name.includes("sales")) {
      byYear[yr].revenue = m.value ?? undefined;
    } else if (name.includes("net income") || name.includes("net profit") || name.includes("pat")) {
      byYear[yr].netIncome = m.value ?? undefined;
    } else if (name.includes("ebitda") || name.includes("operating income")) {
      byYear[yr].ebitda = m.value ?? undefined;
    }
  }

  const chartData = Object.values(byYear).sort((a, b) =>
    a.year.localeCompare(b.year)
  );

  if (isLoading) {
    return (
      <div className="h-72 flex items-end gap-3 px-4 pb-4">
        {[0.6, 0.8, 0.7, 1, 0.9].map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-t-md bg-slate-800 animate-pulse"
            style={{ height: `${h * 100}%` }}
          />
        ))}
      </div>
    );
  }

  // If no multi-year data, show a single bar for current values
  const displayData =
    chartData.length === 0
      ? [{ year: "Current" }]
      : chartData;

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart
        data={displayData}
        margin={{ top: 8, right: 16, left: 0, bottom: 0 }}
      >
        <defs>
          <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9} />
            <stop offset="100%" stopColor="#1d4ed8" stopOpacity={0.7} />
          </linearGradient>
          <linearGradient id="ebitdaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity={0.85} />
            <stop offset="100%" stopColor="#4338ca" stopOpacity={0.65} />
          </linearGradient>
        </defs>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="rgba(148,163,184,0.08)"
          vertical={false}
        />
        <XAxis
          dataKey="year"
          tick={{ fill: "rgba(148,163,184,0.7)", fontSize: 11 }}
          axisLine={{ stroke: "rgba(148,163,184,0.15)" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "rgba(148,163,184,0.7)", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) =>
            v >= 1000 ? `${(v / 1000).toFixed(0)}K` : `${v}`
          }
          width={42}
        />
        <Tooltip
          content={
            <CustomTooltip
              currencySymbol={currencySymbol}
              unit={unit}
            />
          }
        />
        <Legend
          formatter={(value) => (
            <span className="text-xs text-slate-400">{value}</span>
          )}
        />
        <Bar
          dataKey="revenue"
          name="Revenue"
          fill="url(#revenueGrad)"
          radius={[4, 4, 0, 0]}
          maxBarSize={52}
        />
        <Bar
          dataKey="ebitda"
          name="EBITDA"
          fill="url(#ebitdaGrad)"
          radius={[4, 4, 0, 0]}
          maxBarSize={52}
        />
        <Line
          dataKey="netIncome"
          name="Net Income"
          type="monotone"
          stroke="#10b981"
          strokeWidth={2.5}
          dot={{ fill: "#10b981", r: 4, strokeWidth: 2, stroke: "#064e3b" }}
          activeDot={{ r: 6 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
