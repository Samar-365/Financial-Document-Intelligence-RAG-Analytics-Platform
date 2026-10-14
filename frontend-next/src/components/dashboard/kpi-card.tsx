"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | null;
  yoyChange?: number | null; // percentage e.g. 14.2 means +14.2%
  yoyLabel?: string;
  icon: LucideIcon;
  iconColor?: string;
  accentColor?: string;
  isLoading?: boolean;
  unit?: string;
  description?: string;
}

export function KpiCard({
  title,
  value,
  yoyChange,
  yoyLabel,
  icon: Icon,
  isLoading = false,
  unit,
  description,
}: KpiCardProps) {
  const hasChange = yoyChange !== null && yoyChange !== undefined;
  const isPositive = hasChange && yoyChange! > 0;
  const isNeutral = hasChange && yoyChange! === 0;

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border border-[rgba(196,30,58,0.24)]",
        "bg-[#111017] p-5 shadow-[0_4px_20px_rgba(0,0,0,0.5)]",
        "transition-all duration-300 hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_6px_24px_rgba(184,29,36,0.18)]"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold uppercase tracking-[0.05em] text-[#94A3B8]">
          {title}
        </span>
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[rgba(184,29,36,0.15)] text-[#E63946] border border-[rgba(230,57,70,0.3)]">
          <Icon className="h-4 w-4" />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2 mt-1">
          <div className="h-7 w-28 rounded-md bg-[#1d1b26] animate-pulse" />
          <div className="h-4 w-20 rounded-md bg-[#1d1b26]/70 animate-pulse" />
        </div>
      ) : (
        <>
          <div className="text-2xl font-bold tracking-tight text-white">
            {value ?? "N/A"}
            {unit && (
              <span className="ml-1 text-sm font-medium text-slate-400">
                {unit}
              </span>
            )}
          </div>

          {description && !hasChange && (
            <p className="mt-1 text-xs text-slate-500">{description}</p>
          )}

          {hasChange && (
            <div
              className={cn(
                "mt-2 flex items-center gap-1 text-xs font-semibold",
                isPositive
                  ? "text-emerald-400"
                  : isNeutral
                  ? "text-slate-400"
                  : "text-[#E63946]"
              )}
            >
              {isPositive ? (
                <TrendingUp className="h-3.5 w-3.5" />
              ) : isNeutral ? (
                <Minus className="h-3.5 w-3.5" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5" />
              )}
              {isPositive ? "+" : ""}
              {yoyChange!.toFixed(1)}% {yoyLabel ?? "YoY"}
            </div>
          )}
        </>
      )}
    </div>
  );
}
