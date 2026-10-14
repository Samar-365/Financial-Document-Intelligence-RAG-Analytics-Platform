"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { WorkspaceSelector } from "@/components/shared/workspace-selector";
import { SystemHealth } from "@/components/shared/system-health";
import {
  LayoutDashboard,
  FolderUp,
  LineChart,
  Bot,
  GitCompare,
  ShieldCheck,
  Activity,
  LucideIcon,
} from "lucide-react";

const ROUTE_CONFIG: Record<
  string,
  { title: string; subtitle: string; icon: LucideIcon }
> = {
  "/dashboard": {
    title: "Executive Financial Dashboard",
    subtitle: "Continuous extraction, 5-dimension corporate health monitoring, and interactive financial performance bridges.",
    icon: LayoutDashboard,
  },
  "/documents": {
    title: "Document & Dataset Ingestion",
    subtitle: "Upload corporate filings and spreadsheet datasets across PDF, CSV, and Excel (.xlsx) formats for vector indexing.",
    icon: FolderUp,
  },
  "/analysis": {
    title: "Financial Statement Analysis",
    subtitle: "Deep-dive into P&L, Balance Sheet, Cash Flow, and Ind AS metrics with confidence scoring.",
    icon: LineChart,
  },
  "/chat": {
    title: "AI Financial Analyst",
    subtitle: "Financial intelligence for the selected document with verifiable page-level citations.",
    icon: Bot,
  },
  "/compare": {
    title: "Document Comparison",
    subtitle: "Compare two processed financial reports side-by-side with automated delta calculations and visual analytics.",
    icon: GitCompare,
  },
  "/audit": {
    title: "System Telemetry & Audit Logs",
    subtitle: "Live monitoring of API health probes, pgvector database status, and processing audit logs.",
    icon: ShieldCheck,
  },
};

export function Header() {
  const pathname = usePathname();
  const currentRoute =
    Object.entries(ROUTE_CONFIG).find(([path]) => pathname.startsWith(path))?.[1] || {
      title: "FinDoc Platform",
      subtitle: "Financial Document Intelligence & RAG Analytics",
      icon: Activity,
    };

  const Icon = currentRoute.icon;

  return (
    <header className="sticky top-0 z-20 flex h-20 w-full items-center justify-between border-b border-[rgba(184,29,36,0.25)] bg-[#0D0C12]/95 px-6 backdrop-blur-xl">
      {/* Route Title & Subtitle with Wine Red Icon Badge */}
      <div className="flex items-center gap-3.5 min-w-0">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.15)] border border-[rgba(196,30,58,0.4)] shadow-[0_0_15px_rgba(184,29,36,0.2)] text-[#E63946]">
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex flex-col min-w-0">
          <h1 className="text-lg font-bold tracking-tight text-white truncate leading-tight">
            {currentRoute.title}
          </h1>
          <p className="text-xs text-[#94A3B8] hidden lg:block truncate max-w-xl mt-0.5">
            {currentRoute.subtitle}
          </p>
        </div>
      </div>

      {/* Global Controls */}
      <div className="flex items-center gap-3 shrink-0">
        <WorkspaceSelector />
        <div className="h-4 w-[1px] bg-slate-800 hidden sm:block" />
        <SystemHealth />
      </div>
    </header>
  );
}
