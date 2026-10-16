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
  totalChunks: _totalChunks = 0,
  latencyMs,
}: TelemetryCardsProps) {
  const isHealthy = health?.status === "healthy" || health?.status === "ok";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* FastAPI Probe */}
      <Card className="border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none hover:shadow-[6px_6px_0px_#000000] transition-shadow">
        <CardHeader className="border-b border-black pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-[10px] uppercase font-mono tracking-widest text-zinc-600 font-bold">
            FASTAPI GATEWAY
          </CardTitle>
          <Activity className="h-4 w-4 text-black" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircle2 className="h-5 w-5 text-black shrink-0" />
            ) : (
              <XCircle className="h-5 w-5 text-[#FF0000] shrink-0" />
            )}
            <span
              className={`text-lg font-black uppercase ${
                isHealthy ? "text-black" : "text-[#FF0000]"
              }`}
            >
              {isHealthy ? "200 OK ONLINE" : "DISCONNECTED"}
            </span>
          </div>
          <p className="text-[10px] font-mono text-zinc-600 mt-2 flex items-center gap-1 uppercase">
            <Clock className="h-3 w-3 text-black" />
            PROBE LATENCY: {latencyMs !== undefined ? `${latencyMs}MS` : "—"}
          </p>
        </CardContent>
      </Card>

      {/* Database Status */}
      <Card className="border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none hover:shadow-[6px_6px_0px_#000000] transition-shadow">
        <CardHeader className="border-b border-black pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-[10px] uppercase font-mono tracking-widest text-zinc-600 font-bold">
            POSTGRESQL 16
          </CardTitle>
          <Database className="h-4 w-4 text-[#FF0000]" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-lg font-black uppercase text-black flex items-center gap-2">
            <span className="h-2 w-2 bg-black inline-block" />
            <span>3NF SCHEMAS ACTIVE</span>
          </div>
          <p className="text-[10px] font-mono text-zinc-600 mt-2 uppercase">
            CORPUS ENTITIES: {totalDocuments} INDEXED FILINGS
          </p>
        </CardContent>
      </Card>

      {/* Vector Index */}
      <Card className="border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none hover:shadow-[6px_6px_0px_#000000] transition-shadow">
        <CardHeader className="border-b border-black pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-[10px] uppercase font-mono tracking-widest text-zinc-600 font-bold">
            PGVECTOR EMBEDDINGS
          </CardTitle>
          <Cpu className="h-4 w-4 text-black" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-lg font-black uppercase text-black">1536-DIM COSINE</div>
          <p className="text-[10px] font-mono text-zinc-600 mt-2 uppercase">
            HNSW INDEX • M=16, EF=64
          </p>
        </CardContent>
      </Card>

      {/* Extraction Guard */}
      <Card className="border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none hover:shadow-[6px_6px_0px_#000000] transition-shadow">
        <CardHeader className="border-b border-black pb-2 flex flex-row items-center justify-between">
          <CardTitle className="text-[10px] uppercase font-mono tracking-widest text-zinc-600 font-bold">
            AUDIT GOVERNANCE
          </CardTitle>
          <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 border border-black bg-black text-white font-bold">
            STRICT
          </span>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-lg font-black uppercase text-black">GROUNDED RAG</div>
          <p className="text-[10px] font-mono text-zinc-600 mt-2 uppercase">
            REFUSAL RULE ON MISSING SOURCES
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
