"use client";

import React from "react";
import { ShieldCheck, ShieldAlert, AlertTriangle, Info } from "lucide-react";
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
    icon: AlertTriangle,
    color: "text-[#FF0000]",
    border: "border-black bg-white hover:shadow-[3px_3px_0px_#FF0000]",
    badge: "bg-[#FF0000] text-white border-black",
  },
  MEDIUM: {
    icon: AlertTriangle,
    color: "text-black",
    border: "border-black bg-white hover:shadow-[3px_3px_0px_#000000]",
    badge: "bg-black text-white border-black",
  },
  INFO: {
    icon: Info,
    color: "text-black",
    border: "border-black bg-white hover:shadow-[3px_3px_0px_#000000]",
    badge: "bg-white text-black border-black",
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
    <div className="flex flex-col gap-4">
      {/* Score Summary */}
      <div className="rounded-none border border-black bg-white p-5 shadow-[4px_4px_0px_#000000]">
        <div className="flex items-center justify-between mb-3 border-b border-black pb-2">
          <h4 className="text-xs font-black uppercase tracking-widest text-black flex items-center gap-2">
            <span className="text-[#FF0000]">[ 01 ]</span> AUDIT PROVENANCE
          </h4>
          <span className="text-[10px] font-mono text-zinc-600 uppercase">SYSTEM TRACE</span>
        </div>
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-4 w-full bg-zinc-200 animate-pulse" />
            ))}
          </div>
        ) : (
          <ul className="space-y-2.5 text-xs font-mono">
            {documentName && (
              <li className="flex justify-between items-center gap-4">
                <span className="text-zinc-600 uppercase">FILING:</span>
                <code className="text-black bg-zinc-100 px-2 py-0.5 border border-black truncate max-w-[220px]">
                  {documentName}
                </code>
              </li>
            )}
            <li className="flex justify-between items-center">
              <span className="text-zinc-600 uppercase">HEALTH SCORE:</span>
              <span className="font-black text-black text-sm">
                {overallScore !== null ? `${overallScore.toFixed(1)} / 100` : "N/A"}
              </span>
            </li>
            <li className="flex justify-between items-center">
              <span className="text-zinc-600 uppercase">DATABASE:</span>
              <span className="text-black font-bold">PostgreSQL 16 + pgvector</span>
            </li>
            <li className="flex justify-between items-center">
              <span className="text-zinc-600 uppercase">INFERENCE ENGINE:</span>
              <span className="text-black font-bold">Google Gemini 1.5</span>
            </li>
          </ul>
        )}
      </div>

      {/* Risk Flags */}
      <div className="rounded-none border border-black bg-white p-5 shadow-[4px_4px_0px_#000000] flex-1">
        <div className="flex items-center justify-between mb-3 border-b border-black pb-2">
          <h4 className="text-xs font-black uppercase tracking-widest text-black flex items-center gap-2">
            <span className="text-[#FF0000]">[ 02 ]</span> RISK INDICATORS
          </h4>
          <span className="text-[10px] font-mono text-zinc-600 uppercase">EXCEPTIONS</span>
        </div>
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div key={i} className="h-12 bg-zinc-200 animate-pulse" />
            ))}
          </div>
        ) : noRisks ? (
          <div className="flex items-center gap-3 border border-black bg-white p-4">
            <ShieldCheck className="h-5 w-5 text-black shrink-0" />
            <p className="text-xs font-mono uppercase tracking-wider text-black">
              No material solvency or financial distress flags detected in corpus.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {parsed.map((flag, idx) => {
              const cfg = severityConfig[flag.severity];
              const SeverityIcon = cfg.icon;
              return (
                <div
                  key={idx}
                  className={cn(
                    "flex items-start gap-3 border p-3 transition-shadow duration-150",
                    cfg.border
                  )}
                >
                  <SeverityIcon className={cn("h-4 w-4 mt-0.5 shrink-0", cfg.color)} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={cn(
                          "inline-flex items-center border px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider",
                          cfg.badge
                        )}
                      >
                        {flag.severity}
                      </span>
                      <span className="text-xs font-black uppercase text-black">
                        {flag.category}
                      </span>
                    </div>
                    <p className="text-xs font-mono text-zinc-700 leading-relaxed">
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
