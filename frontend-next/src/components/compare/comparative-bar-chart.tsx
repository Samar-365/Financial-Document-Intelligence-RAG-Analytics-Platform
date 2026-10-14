"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { DeltaItem } from "@/types/comparison";
import { TrendingUp, BarChart2 } from "lucide-react";

interface ComparativeBarChartProps {
  deltas: DeltaItem[];
  docAId: string;
  docBId: string;
  docAName: string;
  docBName: string;
  currencySymbol?: string;
  unit?: string;
}

export function ComparativeBarChart({
  deltas,
  docAId,
  docBId,
  docAName,
  docBName,
  currencySymbol = "₹",
  unit = "Cr",
}: ComparativeBarChartProps) {
  // Format data for chart
  const chartData = deltas.map((d) => {
    const valA = d.values?.[docAId] ?? 0;
    const valB = d.values?.[docBId] ?? 0;
    return {
      metric: d.metric_name,
      [docAName]: valA,
      [docBName]: valB,
      pctDelta: d.percent_delta,
    };
  });

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item = chartData.find((c) => c.metric === label);
      const pct = item?.pctDelta ?? 0;
      return (
        <div className="rounded-xl border border-[rgba(196,30,58,0.35)] bg-[#111017] p-3.5 shadow-2xl text-xs space-y-2">
          <p className="font-bold text-white border-b border-[rgba(196,30,58,0.2)] pb-1">
            {label}
          </p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <span className="flex items-center gap-1.5" style={{ color: entry.color }}>
                  <span
                    className="h-2 w-2 rounded-full inline-block"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span>{entry.name}:</span>
                </span>
                <span className="font-mono font-semibold text-white">
                  {currencySymbol}
                  {Number(entry.value).toLocaleString(undefined, { maximumFractionDigits: 1 })}{" "}
                  {unit}
                </span>
              </div>
            ))}
          </div>
          <div className="pt-1 border-t border-[rgba(196,30,58,0.2)] flex justify-between items-center text-[11px]">
            <span className="text-slate-400">Variance:</span>
            <span
              className={`font-bold font-mono ${
                pct > 0 ? "text-emerald-400" : pct < 0 ? "text-[#FF6B6B]" : "text-slate-400"
              }`}
            >
              {pct > 0 ? "+" : ""}
              {pct.toFixed(2)}%
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-5 shadow-xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart2 className="h-4 w-4 text-[#E63946]" />
          <h4 className="text-sm font-bold text-white">Comparative Metric Trajectory</h4>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Normalized in {unit} ({currencySymbol})
        </span>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(184, 29, 36, 0.15)" opacity={0.6} />
            <XAxis
              dataKey="metric"
              stroke="#94A3B8"
              fontSize={11}
              angle={-20}
              textAnchor="end"
              tickLine={false}
            />
            <YAxis
              stroke="#94A3B8"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 10, fontSize: "12px" }}
              iconType="circle"
            />
            <Bar
              dataKey={docAName}
              fill="#800020"
              radius={[4, 4, 0, 0]}
              maxBarSize={45}
            />
            <Bar
              dataKey={docBName}
              fill="#E63946"
              radius={[4, 4, 0, 0]}
              maxBarSize={45}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
