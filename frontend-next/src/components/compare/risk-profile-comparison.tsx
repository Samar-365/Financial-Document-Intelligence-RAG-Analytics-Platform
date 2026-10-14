"use client";

import React from "react";
import { HealthScoreResponse } from "@/types/financial";
import { AlertTriangle, ShieldCheck, CheckCircle2, TrendingUp, AlertCircle } from "lucide-react";

interface RiskProfileComparisonProps {
  healthA: HealthScoreResponse | null;
  healthB: HealthScoreResponse | null;
  docAName: string;
  docBName: string;
}

function getScoreRating(score: number | null, rating?: string): string {
  if (rating) return rating;
  if (score === null) return "—";
  if (score >= 80) return "Strong";
  if (score >= 65) return "Stable";
  if (score >= 50) return "Moderate";
  if (score >= 35) return "Fragile";
  return "Distressed";
}

export function RiskProfileComparison({
  healthA,
  healthB,
  docAName,
  docBName,
}: RiskProfileComparisonProps) {
  const scoreA = healthA?.overall_score ?? null;
  const scoreB = healthB?.overall_score ?? null;
  const deltaScore = scoreA !== null && scoreB !== null ? scoreB - scoreA : null;

  // Extract risk flags
  const flagsA = new Set(
    (healthA?.risk_flags || []).map((f) =>
      typeof f === "string" ? f : (f as { description?: string }).description || JSON.stringify(f)
    )
  );

  const flagsB = new Set(
    (healthB?.risk_flags || []).map((f) =>
      typeof f === "string" ? f : (f as { description?: string }).description || JSON.stringify(f)
    )
  );

  // Set arithmetic
  const newlyEmergedRisks = Array.from(flagsB).filter((x) => !flagsA.has(x));
  const resolvedRisks = Array.from(flagsA).filter((x) => !flagsB.has(x));
  const persistentRisks = Array.from(flagsA).filter((x) => flagsB.has(x));

  const ratingA = getScoreRating(scoreA, healthA?.rating);
  const ratingB = getScoreRating(scoreB, healthB?.rating);

  return (
    <div className="rounded-2xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-5 shadow-xl backdrop-blur-md space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-[#E63946]" />
          <h4 className="text-sm font-bold text-white">
            Health Trajectory &amp; Risk Factor Comparison
          </h4>
        </div>
        <span className="text-xs text-slate-400">
          Composite 5D Health Scoring &amp; Risk Flag Drift
        </span>
      </div>

      {/* Health Score Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Baseline Card */}
        <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#14131D] p-4 space-y-1">
          <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
            Baseline Health ({docAName})
          </span>
          <div className="text-2xl font-bold text-white">
            {scoreA !== null ? `${scoreA.toFixed(1)}/100` : "N/A"}
          </div>
          <p className="text-xs text-slate-400 font-medium">
            Rating: <span className="text-[#E63946] font-semibold">{ratingA}</span>
          </p>
        </div>

        {/* Target Card */}
        <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#14131D] p-4 space-y-1">
          <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
            Target Health ({docBName})
          </span>
          <div className="text-2xl font-bold text-white flex items-center justify-between">
            <span>{scoreB !== null ? `${scoreB.toFixed(1)}/100` : "N/A"}</span>
            {deltaScore !== null && (
              <span
                className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${
                  deltaScore >= 0
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "bg-[rgba(184,29,36,0.2)] text-[#FF6B6B] border border-[rgba(230,57,70,0.4)]"
                }`}
              >
                {deltaScore >= 0 ? "+" : ""}
                {deltaScore.toFixed(1)} pts
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 font-medium">
            Rating: <span className="text-[#FF4D6D] font-semibold">{ratingB}</span>
          </p>
        </div>

        {/* Risk Drift Summary Card */}
        <div className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#14131D] p-4 space-y-1">
          <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
            Risk Factor Drift
          </span>
          <div className="text-2xl font-bold text-amber-400">
            {newlyEmergedRisks.length} New
          </div>
          <p className="text-xs text-slate-400">
            {resolvedRisks.length} mitigated • {persistentRisks.length} recurring
          </p>
        </div>
      </div>

      {/* Risk Items Breakdown */}
      <div className="space-y-3 pt-2">
        {/* Newly Emerged Risks */}
        {newlyEmergedRisks.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5" />
              Newly Emerged Risk Disclosures ({newlyEmergedRisks.length})
            </span>
            <div className="space-y-1.5">
              {newlyEmergedRisks.map((risk, idx) => (
                <div
                  key={`new-risk-${idx}`}
                  className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3.5 py-2 text-xs text-slate-200 leading-relaxed"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mitigated Risks */}
        {resolvedRisks.length > 0 && (
          <div className="space-y-1.5 pt-2">
            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Resolved / Mitigated Risk Factors ({resolvedRisks.length})
            </span>
            <div className="space-y-1.5">
              {resolvedRisks.map((risk, idx) => (
                <div
                  key={`res-risk-${idx}`}
                  className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-2 text-xs text-slate-300 leading-relaxed"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Persistent Risks */}
        {persistentRisks.length > 0 && (
          <div className="space-y-1.5 pt-2">
            <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
              <AlertCircle className="h-3.5 w-3.5 text-slate-500" />
              Persistent Disclosures Across Both Filings ({persistentRisks.length})
            </span>
            <div className="space-y-1.5">
              {persistentRisks.map((risk, idx) => (
                <div
                  key={`pers-risk-${idx}`}
                  className="rounded-lg border border-slate-800 bg-slate-950/60 px-3.5 py-2 text-xs text-slate-400 leading-relaxed"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {newlyEmergedRisks.length === 0 && resolvedRisks.length === 0 && persistentRisks.length === 0 && (
          <p className="text-xs text-slate-500 italic">
            No specific risk flags cataloged for these filings.
          </p>
        )}
      </div>
    </div>
  );
}
