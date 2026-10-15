"use client";

import React from "react";
import { HealthScoreResponse } from "@/types/financial";
import { AlertTriangle, ShieldCheck, CheckCircle2, AlertCircle } from "lucide-react";

interface RiskProfileComparisonProps {
  healthA: HealthScoreResponse | null;
  healthB: HealthScoreResponse | null;
  docAName: string;
  docBName: string;
}

function getScoreRating(score: number | null, rating?: string): string {
  if (rating) return rating;
  if (score === null) return "—";
  if (score >= 80) return "STRONG";
  if (score >= 65) return "STABLE";
  if (score >= 50) return "MODERATE";
  if (score >= 35) return "FRAGILE";
  return "DISTRESSED";
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
    <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-black pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-[#FF0000]" />
          <h4 className="text-xs font-black uppercase tracking-wider text-black">
            <span className="text-[#FF0000]">[ 03 / RISK ]</span> HEALTH TRAJECTORY &amp; RISK DRIFT
          </h4>
        </div>
        <span className="text-[10px] font-mono text-zinc-500 uppercase">
          COMPOSITE 5D HEALTH SCORING &amp; DISCLOSURE DRIFT
        </span>
      </div>

      {/* Health Score Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Baseline Card */}
        <div className="border border-black bg-white p-4 space-y-1 shadow-[2px_2px_0px_#000000]">
          <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-zinc-600">
            BASELINE ({docAName})
          </span>
          <div className="text-3xl font-black text-black">
            {scoreA !== null ? `${scoreA.toFixed(1)}/100` : "N/A"}
          </div>
          <p className="text-xs font-mono text-zinc-600 uppercase">
            RATING: <span className="text-black font-bold">{ratingA}</span>
          </p>
        </div>

        {/* Target Card */}
        <div className="border border-black bg-white p-4 space-y-1 shadow-[2px_2px_0px_#000000]">
          <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-zinc-600">
            TARGET ({docBName})
          </span>
          <div className="text-3xl font-black text-black flex items-center justify-between">
            <span>{scoreB !== null ? `${scoreB.toFixed(1)}/100` : "N/A"}</span>
            {deltaScore !== null && (
              <span
                className={`text-xs font-mono font-bold px-2 py-0.5 border border-black ${
                  deltaScore >= 0
                    ? "bg-black text-white"
                    : "bg-[#FF0000] text-white"
                }`}
              >
                {deltaScore >= 0 ? "+" : ""}
                {deltaScore.toFixed(1)} PTS
              </span>
            )}
          </div>
          <p className="text-xs font-mono text-zinc-600 uppercase">
            RATING: <span className="text-[#FF0000] font-bold">{ratingB}</span>
          </p>
        </div>

        {/* Risk Drift Summary Card */}
        <div className="border border-black bg-white p-4 space-y-1 shadow-[2px_2px_0px_#000000]">
          <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-zinc-600">
            DISCLOSURE DRIFT DELTA
          </span>
          <div className="text-3xl font-black text-black">
            {newlyEmergedRisks.length} NEW
          </div>
          <p className="text-xs font-mono text-zinc-600 uppercase">
            {resolvedRisks.length} RESOLVED • {persistentRisks.length} RECURRING
          </p>
        </div>
      </div>

      {/* Risk Items Breakdown */}
      <div className="space-y-4 pt-2">
        {/* Newly Emerged Risks */}
        {newlyEmergedRisks.length > 0 && (
          <div className="space-y-2">
            <span className="text-xs font-black uppercase text-[#FF0000] flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5" />
              NEWLY EMERGED RISK DISCLOSURES ({newlyEmergedRisks.length})
            </span>
            <div className="space-y-2">
              {newlyEmergedRisks.map((risk, idx) => (
                <div
                  key={`new-risk-${idx}`}
                  className="border border-black bg-white p-3 text-xs font-mono uppercase text-black leading-relaxed shadow-[2px_2px_0px_#FF0000]"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mitigated Risks */}
        {resolvedRisks.length > 0 && (
          <div className="space-y-2 pt-2">
            <span className="text-xs font-black uppercase text-black flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" />
              RESOLVED / MITIGATED RISK FACTORS ({resolvedRisks.length})
            </span>
            <div className="space-y-2">
              {resolvedRisks.map((risk, idx) => (
                <div
                  key={`res-risk-${idx}`}
                  className="border border-black bg-zinc-50 p-3 text-xs font-mono uppercase text-zinc-800 leading-relaxed"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Persistent Risks */}
        {persistentRisks.length > 0 && (
          <div className="space-y-2 pt-2">
            <span className="text-xs font-black uppercase text-zinc-600 flex items-center gap-1.5">
              <AlertCircle className="h-3.5 w-3.5" />
              PERSISTENT DISCLOSURES ACROSS BOTH FILINGS ({persistentRisks.length})
            </span>
            <div className="space-y-2">
              {persistentRisks.map((risk, idx) => (
                <div
                  key={`pers-risk-${idx}`}
                  className="border border-zinc-300 bg-white p-3 text-xs font-mono uppercase text-zinc-600 leading-relaxed"
                >
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {newlyEmergedRisks.length === 0 && resolvedRisks.length === 0 && persistentRisks.length === 0 && (
          <p className="text-xs font-mono uppercase text-zinc-500">
            NO SPECIFIC RISK FLAGS CATALOGED FOR THESE ENTITY FILINGS.
          </p>
        )}
      </div>
    </div>
  );
}
