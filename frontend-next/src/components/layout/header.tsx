"use client";

import React from "react";
import { usePathname } from "next/navigation";
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
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-black bg-white px-6 md:px-8">
      {/* Route Title & Subtitle with Minimalist Black/White Badge */}
      <div className="flex items-center gap-4 min-w-0">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center border border-black bg-black text-white">
          <Icon className="h-4.5 w-4.5" />
        </div>
        <div className="flex flex-col min-w-0">
          <h1 className="text-base font-black uppercase tracking-tight text-black truncate leading-tight">
            {currentRoute.title}
          </h1>
          <p className="text-[11px] font-mono uppercase tracking-wider text-neutral-500 hidden lg:block truncate max-w-xl">
            {currentRoute.subtitle}
          </p>
        </div>
      </div>

    </header>
  );
}
