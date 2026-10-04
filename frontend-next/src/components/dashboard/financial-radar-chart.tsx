"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface DimensionScores {
  growth_score?: number | null;
  profitability_score?: number | null;
  liquidity_score?: number | null;
  leverage_score?: number | null;
  cash_flow_score?: number | null;
}

interface FinancialRadarProps {
  scores: DimensionScores;
  isLoading?: boolean;
}

// Custom Tooltip
const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: { subject: string; value: number } }[];
}) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div className="rounded-lg border border-slate-700/80 bg-slate-900/95 px-3 py-2 text-xs shadow-2xl">
        <p className="font-semibold text-white mb-0.5">{d.subject}</p>
        <p className="text-blue-400 font-bold">{d.value.toFixed(1)} / 100</p>
      </div>
    );
  }
  return null;
};

export function FinancialRadarChart({
  scores,
  isLoading = false,
}: FinancialRadarProps) {
  const data = [
    {
      subject: "Growth",
      value: scores.growth_score ?? 0,
      fullMark: 100,
    },
    {
      subject: "Profitability",
      value: scores.profitability_score ?? 0,
      fullMark: 100,
    },
    {
      subject: "Liquidity",
      value: scores.liquidity_score ?? 0,
      fullMark: 100,
    },
    {
      subject: "Leverage",
      value: scores.leverage_score ?? 0,
      fullMark: 100,
    },
    {
      subject: "Cash Flow",
      value: scores.cash_flow_score ?? 0,
      fullMark: 100,
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-48 w-48 rounded-full bg-slate-800/60 animate-pulse" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart cx="50%" cy="50%" outerRadius="72%" data={data}>
        <defs>
          <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#6366f1" stopOpacity={0.08} />
          </radialGradient>
        </defs>
        <PolarGrid stroke="rgba(148,163,184,0.15)" />
        <PolarAngleAxis
          dataKey="subject"
          tick={{ fill: "rgba(148,163,184,0.8)", fontSize: 11, fontWeight: 600 }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Radar
          name="Score"
          dataKey="value"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#radarFill)"
          dot={{ r: 4, fill: "#3b82f6", strokeWidth: 2, stroke: "#1e40af" }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
