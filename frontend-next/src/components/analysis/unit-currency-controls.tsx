"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { IndianRupee, DollarSign } from "lucide-react";

const UNITS = ["Cr", "Mn", "Bn", "K"] as const;
type Unit = (typeof UNITS)[number];

const UNIT_LABELS: Record<Unit, string> = {
  Cr: "Crores",
  Mn: "Millions",
  Bn: "Billions",
  K: "Thousands",
};

export function UnitCurrencyControls() {
  const { currency, unit, setCurrency, setUnit } = useWorkspaceStore();

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Currency Toggle */}
      <div className="flex items-center rounded-lg border border-slate-700/60 bg-slate-900/60 p-0.5">
        <button
          id="currency-inr"
          onClick={() => setCurrency("INR")}
          className={cn(
            "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-all",
            currency === "INR"
              ? "bg-blue-600 text-white shadow-md shadow-blue-500/25"
              : "text-slate-400 hover:text-white"
          )}
        >
          <IndianRupee className="h-3 w-3" />
          INR
        </button>
        <button
          id="currency-usd"
          onClick={() => setCurrency("USD")}
          className={cn(
            "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-all",
            currency === "USD"
              ? "bg-blue-600 text-white shadow-md shadow-blue-500/25"
              : "text-slate-400 hover:text-white"
          )}
        >
          <DollarSign className="h-3 w-3" />
          USD
        </button>
      </div>

      {/* Unit Toggle */}
      <div className="flex items-center rounded-lg border border-slate-700/60 bg-slate-900/60 p-0.5">
        {UNITS.map((u) => (
          <button
            key={u}
            id={`unit-${u.toLowerCase()}`}
            onClick={() => setUnit(u)}
            title={UNIT_LABELS[u]}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-semibold transition-all",
              unit === u
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/25"
                : "text-slate-400 hover:text-white"
            )}
          >
            {u}
          </button>
        ))}
      </div>

      {/* Current label */}
      <span className="text-xs text-slate-500 hidden sm:block">
        Displaying in{" "}
        <span className="text-slate-300 font-medium">
          {currency === "INR" ? "₹" : "$"} {UNIT_LABELS[unit as Unit] ?? unit}
        </span>
      </span>
    </div>
  );
}
