"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderUp,
  LineChart,
  Bot,
  GitCompare,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Layers,
  FileSpreadsheet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  {
    name: "Executive Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: "Document Ingestion",
    href: "/documents",
    icon: FolderUp,
    badge: "Upload",
  },
  {
    name: "Financial Analysis",
    href: "/analysis",
    icon: LineChart,
    badge: "Ind AS",
  },
  {
    name: "AI Analyst (RAG)",
    href: "/chat",
    icon: Bot,
    badge: "AI",
    isGlowing: true,
  },
  {
    name: "Peer Benchmarking",
    href: "/compare",
    icon: GitCompare,
    badge: null,
  },
  {
    name: "Audit & Governance",
    href: "/audit",
    icon: ShieldCheck,
    badge: null,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl transition-all duration-300 z-30",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/60">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 overflow-hidden group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-all">
            <Layers className="h-5 w-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                FinDoc
              </span>
              <span className="text-[10px] uppercase font-semibold tracking-wider text-blue-400">
                Intelligence Platform
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {!collapsed && (
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Platform Modules
          </p>
        )}
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              )}
              title={collapsed ? item.name : undefined}
            >
              <Icon
                className={cn(
                  "h-5 w-5 shrink-0 transition-transform group-hover:scale-110",
                  isActive
                    ? "text-blue-400"
                    : "text-slate-500 group-hover:text-slate-300",
                  item.isGlowing && isActive && "text-cyan-400"
                )}
              />
              {!collapsed && (
                <span className="flex-1 truncate">{item.name}</span>
              )}
              {!collapsed && item.badge && (
                <span
                  className={cn(
                    "text-[10px] font-semibold px-2 py-0.5 rounded-full border",
                    item.isGlowing
                      ? "border-cyan-500/40 bg-cyan-500/15 text-cyan-300"
                      : "border-slate-700 bg-slate-800 text-slate-400"
                  )}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Footer Info Card */}
      {!collapsed && (
        <div className="p-3 border-t border-slate-800/60">
          <div className="rounded-lg border border-slate-800/80 bg-slate-900/50 p-3 text-xs">
            <div className="flex items-center gap-2 text-slate-300 font-semibold mb-1">
              <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
              <span>Ind AS & RAG Engine</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Autonomous extraction & vector retrieval powered by pgvector.
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
