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
        "group relative border border-black bg-white p-3.5 sm:p-4 rounded-none",
        "transition-all duration-150 hover:shadow-[4px_4px_0px_#000000] hover:-translate-x-0.5 hover:-translate-y-0.5"
      )}
    >
      <div className="flex items-center justify-between gap-1.5 pb-2 border-b-2 border-black">
        <span className="text-xs sm:text-[12.5px] font-sans font-black uppercase tracking-wider text-black [-webkit-text-stroke:0.35px_#000000]" title={title}>
          [ {title} ]
        </span>
        <div className="flex h-5 w-5 shrink-0 items-center justify-center border-2 border-black bg-white text-black group-hover:bg-black group-hover:text-white transition-colors">
          <Icon size={12} strokeWidth={2.5} className="shrink-0" />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2 mt-4">
          <div className="h-10 w-32 bg-neutral-200 animate-pulse" />
          <div className="h-4 w-20 bg-neutral-200 animate-pulse" />
        </div>
      ) : (
        <div className="mt-3">
          <div className="text-3xl sm:text-4xl lg:text-[40px] font-black tracking-tighter text-black leading-none">
            {value ?? "N/A"}
            {unit && (
              <span className="ml-1.5 text-xs font-mono font-black uppercase text-neutral-700">
                {unit}
              </span>
            )}
          </div>

          {description && !hasChange && (
            <p className="mt-2 text-xs font-mono font-bold text-neutral-700">{description}</p>
          )}

          {hasChange && (
            <div className="mt-3 flex items-center gap-1.5">
              <span
                className={cn(
                  "inline-flex items-center gap-1 font-mono text-[10px] font-bold px-1.5 py-0.5 border",
                  isPositive
                    ? "border-black bg-black text-white"
                    : isNeutral
                    ? "border-neutral-300 text-neutral-600"
                    : "border-[#FF0000] bg-[#FF0000] text-white"
                )}
              >
                {isPositive ? (
                  <TrendingUp className="h-3 w-3" />
                ) : isNeutral ? (
                  <Minus className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {isPositive ? "+" : ""}
                {yoyChange!.toFixed(1)}% {yoyLabel ?? "YoY"}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
