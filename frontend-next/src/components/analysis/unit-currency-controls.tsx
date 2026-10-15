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
    <div className="flex flex-wrap items-center gap-2">
      {/* Currency Toggle */}
      <div className="flex items-center border border-black bg-white p-0.5 shadow-[2px_2px_0px_#000000]">
        <button
          id="currency-inr"
          onClick={() => setCurrency("INR")}
          className={cn(
            "flex items-center gap-1 px-2.5 py-1 text-[11px] font-mono font-black uppercase transition-all",
            currency === "INR"
              ? "bg-black text-white"
              : "text-black hover:bg-zinc-100"
          )}
        >
          <IndianRupee className="h-3 w-3" />
          INR
        </button>
        <button
          id="currency-usd"
          onClick={() => setCurrency("USD")}
          className={cn(
            "flex items-center gap-1 px-2.5 py-1 text-[11px] font-mono font-black uppercase transition-all",
            currency === "USD"
              ? "bg-black text-white"
              : "text-black hover:bg-zinc-100"
          )}
        >
          <DollarSign className="h-3 w-3" />
          USD
        </button>
      </div>

      {/* Unit Toggle */}
      <div className="flex items-center border border-black bg-white p-0.5 shadow-[2px_2px_0px_#000000]">
        {UNITS.map((u) => (
          <button
            key={u}
            id={`unit-${u.toLowerCase()}`}
            onClick={() => setUnit(u)}
            title={UNIT_LABELS[u]}
            className={cn(
              "px-2.5 py-1 text-[11px] font-mono font-black uppercase transition-all",
              unit === u
                ? "bg-black text-white"
                : "text-black hover:bg-zinc-100"
            )}
          >
            {u}
          </button>
        ))}
      </div>
    </div>
  );
}
