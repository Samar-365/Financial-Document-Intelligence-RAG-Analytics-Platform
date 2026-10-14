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
  Activity,
  Sparkles,
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
        "relative flex flex-col border-r border-[rgba(184,29,36,0.25)] bg-[#0D0C12] transition-all duration-300 z-30 select-none",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-18 items-center justify-between px-4 border-b border-[rgba(184,29,36,0.25)]">
        <Link
          href="/"
          className="flex items-center gap-3 overflow-hidden group py-1"
          title="FinDoc AI Financial Intelligence"
        >
          {/* Official Vector Brand Badge */}
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.2)] border border-[rgba(230,57,70,0.55)] shadow-[0_0_14px_rgba(230,57,70,0.3)] group-hover:scale-105 transition-all">
            <Activity className="h-5 w-5 text-[#E63946]" />
          </div>
          {!collapsed && (
            <div className="flex flex-col text-left">
              <span className="font-extrabold text-lg tracking-tight text-white leading-tight">
                Fin<span className="text-[#E63946]">Doc</span>
              </span>
              <span className="text-[9px] uppercase font-bold tracking-[0.08em] text-[#94A3B8] leading-none mt-0.5">
                Financial Intelligence
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-[rgba(184,29,36,0.3)] bg-[#111017] text-slate-400 hover:text-[#E63946] hover:border-[#E63946] transition-all"
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
      <div className="flex-1 py-4 px-3 space-y-1.5 overflow-y-auto">
        {!collapsed && (
          <p className="px-3 pb-1 text-[10px] font-bold uppercase tracking-[0.08em] text-slate-500">
            Workspace Modules
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
                  ? "bg-[rgba(184,29,36,0.28)] border-l-[3px] border-l-[#E63946] text-white font-semibold shadow-sm"
                  : "text-[#CBD5E1] hover:bg-[rgba(184,29,36,0.15)] hover:text-white"
              )}
              title={collapsed ? item.name : undefined}
            >
              <Icon
                className={cn(
                  "h-4 w-4 shrink-0 transition-transform group-hover:scale-110",
                  isActive
                    ? "text-[#E63946]"
                    : "text-[#94A3B8] group-hover:text-[#E63946]"
                )}
              />
              {!collapsed && (
                <span className="flex-1 truncate">{item.name}</span>
              )}
              {!collapsed && item.badge && (
                <span
                  className={cn(
                    "text-[10px] font-bold px-2 py-0.5 rounded-full border",
                    isActive
                      ? "border-[rgba(230,57,70,0.5)] bg-[rgba(184,29,36,0.35)] text-white"
                      : "border-[rgba(196,30,58,0.3)] bg-[rgba(184,29,36,0.15)] text-[#FFA8B2]"
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
        <div className="p-3 border-t border-[rgba(184,29,36,0.25)]">
          <div className="rounded-xl border border-[rgba(184,29,36,0.28)] bg-[#111017] p-3 text-xs shadow-md">
            <div className="flex items-center gap-2 text-white font-bold mb-1">
              <Sparkles className="h-3.5 w-3.5 text-[#E63946]" />
              <span>Pitch Dark & Wine Red</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Autonomous extraction & vector retrieval powered by pgvector.
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
