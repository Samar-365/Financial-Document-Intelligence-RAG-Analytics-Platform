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
import { BarChart2 } from "lucide-react";

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
        <div className="border border-black bg-white p-3 shadow-[4px_4px_0px_#000000] text-xs font-mono space-y-2">
          <p className="font-black text-black uppercase border-b border-black pb-1">
            {label}
          </p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <span className="flex items-center gap-1.5 font-bold uppercase" style={{ color: entry.color }}>
                  <span>{entry.name}:</span>
                </span>
                <span className="font-black text-black">
                  {currencySymbol}
                  {Number(entry.value).toLocaleString(undefined, { maximumFractionDigits: 1 })}{" "}
                  {unit}
                </span>
              </div>
            ))}
          </div>
          <div className="pt-1 border-t border-black flex justify-between items-center text-[10px]">
            <span className="text-zinc-600 uppercase">VARIANCE DELTA:</span>
            <span
              className={`font-black ${
                pct > 0 ? "text-black" : pct < 0 ? "text-[#FF0000]" : "text-zinc-500"
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
    <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-4">
      <div className="flex items-center justify-between border-b border-black pb-3">
        <div className="flex items-center gap-2">
          <BarChart2 className="h-4 w-4 text-black" />
          <h4 className="text-xs font-black uppercase tracking-wider text-black">
            COMPARATIVE TRAJECTORY ANALYSIS
          </h4>
        </div>
        <span className="text-[10px] text-zinc-500 font-mono uppercase">
          NORMALIZED IN {unit} ({currencySymbol})
        </span>
      </div>

      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#E4E4E7" vertical={false} />
            <XAxis
              dataKey="metric"
              stroke="#000000"
              fontSize={10}
              tickLine={true}
              axisLine={{ stroke: "#000000" }}
              angle={-20}
              textAnchor="end"
              height={50}
              tick={{ fill: "#000000", fontWeight: "bold" }}
            />
            <YAxis
              stroke="#000000"
              fontSize={10}
              tickLine={true}
              axisLine={{ stroke: "#000000" }}
              tickFormatter={(val) => `${val >= 1000 ? (val / 1000).toFixed(0) + "k" : val}`}
              tick={{ fill: "#000000" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: 15 }}
              formatter={(value) => (
                <span className="text-[10px] font-mono font-bold uppercase text-black">{value}</span>
              )}
            />
            {/* Baseline bar in pure black */}
            <Bar dataKey={docAName} fill="#000000" radius={[0, 0, 0, 0]} maxBarSize={36} />
            {/* Target bar in statement red */}
            <Bar dataKey={docBName} fill="#FF0000" radius={[0, 0, 0, 0]} maxBarSize={36} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
