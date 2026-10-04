"use client";

import React from "react";
import { ShieldCheck, ShieldAlert, ShieldX, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface RiskFlag {
  category?: string;
  severity?: string;
  description?: string;
  // Raw string case
  raw?: string;
}

interface RiskFlagsCardProps {
  riskFlags: (RiskFlag | string)[];
  overallScore: number | null;
  documentName?: string;
  isLoading?: boolean;
}

function parseRiskFlag(flag: RiskFlag | string): {
  category: string;
  severity: "HIGH" | "MEDIUM" | "INFO";
  description: string;
} {
  if (typeof flag === "string") {
    const text = flag;
    const lower = text.toLowerCase();
    let cat = "SYSTEM";
    let desc = text;
    if (text.includes(":")) {
      [cat, desc] = text.split(":", 2);
      cat = cat.trim();
      desc = desc.trim();
    }
    const severity: "HIGH" | "MEDIUM" | "INFO" =
      lower.includes("high") || lower.includes("critical") || lower.includes("distress")
        ? "HIGH"
        : lower.includes("risk") || lower.includes("warning") || lower.includes("below") || lower.includes("margin")
        ? "MEDIUM"
        : "INFO";
    return { category: cat, severity, description: desc };
  }

  const sev = (String(flag.severity || "INFO").toUpperCase()) as "HIGH" | "MEDIUM" | "INFO";
  return {
    category: flag.category || "RISK",
    severity: ["HIGH", "MEDIUM", "INFO"].includes(sev) ? sev : "INFO",
    description: flag.description || flag.raw || "",
  };
}

const severityConfig = {
  HIGH: {
    icon: ShieldX,
    color: "text-red-400",
    border: "border-red-500/20",
    bg: "bg-red-500/5",
    badge: "bg-red-500/10 text-red-400 border-red-500/30",
  },
  MEDIUM: {
    icon: AlertTriangle,
    color: "text-amber-400",
    border: "border-amber-500/20",
    bg: "bg-amber-500/5",
    badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  },
  INFO: {
    icon: Info,
    color: "text-blue-400",
    border: "border-blue-500/20",
    bg: "bg-blue-500/5",
    badge: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  },
};

export function RiskFlagsCard({
  riskFlags,
  overallScore,
  documentName,
  isLoading = false,
}: RiskFlagsCardProps) {
  const parsed = riskFlags.map(parseRiskFlag);
  const noRisks = !isLoading && parsed.length === 0;

  return (
    <div className="flex flex-col gap-3">
      {/* Score Summary */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md">
        <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">
          Audit Provenance
        </h4>
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-4 w-full rounded bg-slate-800 animate-pulse" />
            ))}
          </div>
        ) : (
          <ul className="space-y-2 text-sm">
            {documentName && (
              <li className="flex justify-between gap-4">
                <span className="text-slate-400">Filing:</span>
                <code className="text-xs text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded truncate max-w-[180px]">
                  {documentName}
                </code>
              </li>
            )}
            <li className="flex justify-between">
              <span className="text-slate-400">Health Score:</span>
              <span className="font-bold text-white">
                {overallScore !== null ? `${overallScore.toFixed(1)} / 100` : "N/A"}
              </span>
            </li>
            <li className="flex justify-between">
              <span className="text-slate-400">DB Engine:</span>
              <span className="text-slate-300 text-xs">PostgreSQL 16 + pgvector</span>
            </li>
            <li className="flex justify-between">
              <span className="text-slate-400">AI Model:</span>
              <span className="text-slate-300 text-xs">Google Gemini</span>
            </li>
          </ul>
        )}
      </div>

      {/* Risk Flags */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md flex-1">
        <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">
          Risk Indicators
        </h4>
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div key={i} className="h-12 rounded-lg bg-slate-800 animate-pulse" />
            ))}
          </div>
        ) : noRisks ? (
          <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3">
            <ShieldCheck className="h-5 w-5 text-emerald-400 shrink-0" />
            <p className="text-sm text-emerald-300 font-medium">
              No material solvency or financial distress flags detected.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {parsed.map((flag, idx) => {
              const cfg = severityConfig[flag.severity];
              const SeverityIcon = cfg.icon;
              return (
                <div
                  key={idx}
                  className={cn(
                    "flex items-start gap-3 rounded-lg border p-3",
                    cfg.border,
                    cfg.bg
                  )}
                >
                  <SeverityIcon className={cn("h-4 w-4 mt-0.5 shrink-0", cfg.color)} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span
                        className={cn(
                          "inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                          cfg.badge
                        )}
                      >
                        {flag.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-300">
                        {flag.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      {flag.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
