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
      <Card className="bg-slate-900/60 border-slate-800 shadow-lg">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            FastAPI Service
          </CardTitle>
          <Activity className="h-4 w-4 text-blue-400" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
            ) : (
              <XCircle className="h-5 w-5 text-rose-400 shrink-0" />
            )}
            <span
              className={`text-lg font-bold ${
                isHealthy ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {isHealthy ? "ONLINE (200 OK)" : "DISCONNECTED"}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Probe Latency: {latencyMs !== undefined ? `${latencyMs}ms` : "—"}
          </p>
        </CardContent>
      </Card>

      {/* Database Status */}
      <Card className="bg-slate-900/60 border-slate-800 shadow-lg">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            PostgreSQL DB
          </CardTitle>
          <Database className="h-4 w-4 text-indigo-400" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-white flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 inline-block animate-pulse" />
            <span>3NF Alpine Active</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Indexed Entities: {totalDocuments} active filings
          </p>
        </CardContent>
      </Card>

      {/* Vector Index */}
      <Card className="bg-slate-900/60 border-slate-800 shadow-lg">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            pgvector HNSW Index
          </CardTitle>
          <Cpu className="h-4 w-4 text-cyan-400" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-cyan-400">384-dim Cosine</div>
          <p className="text-[11px] text-slate-400 mt-1">
            all-MiniLM-L6-v2 • m=16, ef=64
          </p>
        </CardContent>
      </Card>

      {/* Extraction Guard */}
      <Card className="bg-slate-900/60 border-slate-800 shadow-lg">
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-xs uppercase tracking-wider text-slate-400 font-bold">
            Confidence Guard
          </CardTitle>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30">
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
