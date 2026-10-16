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

// Exaggerated Minimalism palette: Solid black, stark white with black stroke, statement red, stark dark gray
const COLORS = {
  equity: "#000000",   // pure black
  debt: "#FF0000",     // statement red
  cash: "#71717A",     // stark gray
  other: "#A1A1AA",
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
      <div className="border-2 border-black bg-white p-3 text-xs font-mono shadow-[4px_4px_0px_#000000] rounded-none min-w-[150px]">
        <div className="flex items-center justify-between border-b-2 border-black pb-1 mb-1.5">
          <span className="font-black uppercase tracking-wider text-xs" style={{ color: entry.payload.color }}>
            [ {entry.name} ]
          </span>
          <span className="inline-block h-2 w-2 border border-black" style={{ background: entry.payload.color }} />
        </div>
        <div className="flex items-baseline justify-between gap-3 pt-0.5">
          <span className="text-[11px] text-zinc-700 font-bold uppercase">VALUE:</span>
          <span className="text-black font-black text-sm">
            {entry.value?.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          </span>
        </div>
      </div>
    );
  }
  return null;
};

export function CapitalDonutChart({
  metrics,
  currencySymbol: _currencySymbol,
  unit: _unit,
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
        <div className="h-44 w-44 rounded-none border-[12px] border-black animate-pulse" />
      </div>
    );
  }

  return (
    <div className="w-full h-64 flex flex-col items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={displayData}
            cx="50%"
            cy="45%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={2}
            dataKey="value"
            stroke="#000000"
            strokeWidth={1.5}
          >
            {displayData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => (
              <span className="text-[11px] font-black uppercase tracking-wider text-black">
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
