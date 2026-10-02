"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { healthService } from "@/lib/services/health-service";
import { Activity } from "lucide-react";

export function SystemHealth() {
  const { data, isError, isLoading } = useQuery({
    queryKey: ["system-health"],
    queryFn: () => healthService.getHealth(),
    refetchInterval: 20000,
    retry: 1,
  });

  const isHealthy = !isError && data?.status === "ok";
  const isDegraded = !isError && data?.status === "degraded";

  return (
    <div
      className="flex items-center gap-2 px-2.5 py-1 rounded-full text-xs border border-slate-800 bg-slate-900/60 backdrop-blur-md transition-all"
      title={`Backend: ${
        isLoading
          ? "Checking..."
          : isHealthy
          ? `Online (v${data?.version || "1.0"})`
          : isDegraded
          ? "Degraded"
          : "Offline"
      }`}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
            isHealthy
              ? "bg-emerald-400"
              : isDegraded
              ? "bg-amber-400"
              : "bg-red-400"
          }`}
        />
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            isHealthy
              ? "bg-emerald-500"
              : isDegraded
              ? "bg-amber-500"
              : "bg-red-500"
          }`}
        />
      </span>
      <span className="font-medium text-slate-300 hidden sm:inline">
        {isLoading
          ? "Connecting..."
          : isHealthy
          ? "System Ready"
          : isDegraded
          ? "Degraded"
          : "Backend Offline"}
      </span>
    </div>
  );
}
