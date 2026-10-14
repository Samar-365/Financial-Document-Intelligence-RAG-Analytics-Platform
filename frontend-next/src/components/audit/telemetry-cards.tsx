"use client";

import React from "react";
import { HealthStatus } from "@/types/health";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, XCircle, Database, Cpu, Activity, Clock } from "lucide-react";

interface TelemetryCardsProps {
  health: HealthStatus | null;
  totalDocuments: number;
  totalChunks?: number;
  latencyMs?: number;
}

export function TelemetryCards({
  health,
  totalDocuments,
  totalChunks = 0,
  latencyMs,
}: TelemetryCardsProps) {
  const isHealthy = health?.status === "healthy" || health?.status === "ok";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* FastAPI Probe */}
      <Card className="pitch-card bg-[#111017] border-[rgba(196,30,58,0.24)] shadow-xl hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_4px_20px_rgba(184,29,36,0.18)] transition-all">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            FastAPI Service
          </CardTitle>
          <Activity className="h-4 w-4 text-[#E63946]" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
            ) : (
              <XCircle className="h-5 w-5 text-[#FF6B6B] shrink-0" />
            )}
            <span
              className={`text-lg font-bold ${
                isHealthy ? "text-emerald-400" : "text-[#FF6B6B]"
              }`}
            >
              {isHealthy ? "ONLINE (200 OK)" : "DISCONNECTED"}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <Clock className="h-3 w-3 text-[#E63946]" />
            Probe Latency: {latencyMs !== undefined ? `${latencyMs}ms` : "—"}
          </p>
        </CardContent>
      </Card>

      {/* Database Status */}
      <Card className="pitch-card bg-[#111017] border-[rgba(196,30,58,0.24)] shadow-xl hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_4px_20px_rgba(184,29,36,0.18)] transition-all">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            PostgreSQL DB
          </CardTitle>
          <Database className="h-4 w-4 text-[#E63946]" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-white flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 inline-block animate-pulse shadow-[0_0_8px_#10B981]" />
            <span>3NF Alpine Active</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Indexed Entities: {totalDocuments} active filings
          </p>
        </CardContent>
      </Card>

      {/* Vector Index */}
      <Card className="pitch-card bg-[#111017] border-[rgba(196,30,58,0.24)] shadow-xl hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_4px_20px_rgba(184,29,36,0.18)] transition-all">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            pgvector HNSW Index
          </CardTitle>
          <Cpu className="h-4 w-4 text-[#E63946]" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-white">384-dim Cosine</div>
          <p className="text-[11px] text-slate-400 mt-1">
            all-MiniLM-L6-v2 • m=16, ef=64
          </p>
        </CardContent>
      </Card>

      {/* Extraction Guard */}
      <Card className="pitch-card bg-[#111017] border-[rgba(196,30,58,0.24)] shadow-xl hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_4px_20px_rgba(184,29,36,0.18)] transition-all">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            Confidence Guard
          </CardTitle>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[rgba(184,29,36,0.2)] text-[#E63946] border border-[rgba(230,57,70,0.4)]">
            Strict
          </span>
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-white">0.45 Min Cutoff</div>
          <p className="text-[11px] text-slate-400 mt-1">
            Rejection filter for low-similarity context
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
