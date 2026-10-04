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
  iconColor = "text-blue-400",
  accentColor = "hover:border-blue-500/40",
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
        "group relative overflow-hidden rounded-xl border border-slate-800/80",
        "bg-slate-900/60 p-5 backdrop-blur-md shadow-xl shadow-black/20",
        "transition-all duration-300",
        accentColor
      )}
    >
      {/* Subtle background glow */}
      <div
        className={cn(
          "absolute -top-8 -right-8 h-24 w-24 rounded-full opacity-0 group-hover:opacity-10 transition-opacity duration-500 blur-2xl",
          iconColor.replace("text-", "bg-")
        )}
      />

      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">
          {title}
        </span>
        <div
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800/80",
            iconColor
          )}
        >
          <Icon className="h-4 w-4" />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2 mt-1">
          <div className="h-7 w-28 rounded-md bg-slate-800 animate-pulse" />
          <div className="h-4 w-20 rounded-md bg-slate-800/70 animate-pulse" />
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
                "mt-1.5 flex items-center gap-1 text-xs font-semibold",
                isPositive
                  ? "text-emerald-400"
                  : isNeutral
                  ? "text-slate-400"
                  : "text-red-400"
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
