"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { WorkspaceSelector } from "@/components/shared/workspace-selector";
import { SystemHealth } from "@/components/shared/system-health";
import { ThemeToggle } from "@/components/shared/theme-toggle";

const ROUTE_NAMES: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Executive Dashboard",
    subtitle: "High-level KPI summaries, financial ratios, and health benchmarks",
  },
  "/documents": {
    title: "Document Ingestion",
    subtitle: "Upload PDF filings, track extraction status, and manage vector indices",
  },
  "/analysis": {
    title: "Financial Statement Analysis",
    subtitle: "Deep-dive into P&L, Balance Sheet, Cash Flow, and Ind AS metrics",
  },
  "/chat": {
    title: "AI Financial Analyst",
    subtitle: "Conversational RAG agent with cited source chunk highlights",
  },
  "/compare": {
    title: "Peer Benchmarking & Comparison",
    subtitle: "Cross-company and multi-period variance analysis",
  },
  "/audit": {
    title: "Audit Logs & Governance",
    subtitle: "System telemetry, extraction confidence logs, and query traces",
  },
};

export function Header() {
  const pathname = usePathname();
  const currentRoute =
    Object.entries(ROUTE_NAMES).find(([path]) => pathname.startsWith(path))?.[1] || {
      title: "FinDoc Platform",
      subtitle: "Financial Document Intelligence & RAG Analytics",
    };

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-6 backdrop-blur-xl">
      {/* Route Title & Subtitle */}
      <div className="flex flex-col">
        <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
          {currentRoute.title}
        </h1>
        <p className="text-xs text-slate-400 hidden xl:block">
          {currentRoute.subtitle}
        </p>
      </div>

      {/* Global Controls */}
      <div className="flex items-center gap-3">
        <WorkspaceSelector />
        <div className="h-4 w-[1px] bg-slate-800 hidden sm:block" />
        <SystemHealth />
        <ThemeToggle />
      </div>
    </header>
  );
}
