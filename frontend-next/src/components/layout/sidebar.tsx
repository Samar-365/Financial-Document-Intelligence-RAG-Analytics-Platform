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
  ArrowUpRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  {
    name: "Dashboard",
    code: "01",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: "Ingestion",
    code: "02",
    href: "/documents",
    icon: FolderUp,
    badge: "UPLOAD",
  },
  {
    name: "Analysis",
    code: "03",
    href: "/analysis",
    icon: LineChart,
    badge: "IND AS",
  },
  {
    name: "AI Analyst",
    code: "04",
    href: "/chat",
    icon: Bot,
    badge: "RAG",
    isGlowing: true,
  },
  {
    name: "Compare",
    code: "05",
    href: "/compare",
    icon: GitCompare,
    badge: null,
  },
  {
    name: "Audit Logs",
    code: "06",
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
        "relative flex flex-col border-r border-black bg-white transition-all duration-200 z-30 select-none",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-black">
        <Link
          href="/"
          className="flex items-center gap-3 overflow-hidden group py-1"
          title="FinDoc AI Financial Intelligence"
        >
          {/* Minimalist Black Box Brand Mark */}
          <div className="flex h-8 w-8 shrink-0 items-center justify-center bg-black text-white transition-all group-hover:bg-[#FF0000]">
            <span className="font-black text-xs tracking-tighter">FD</span>
          </div>
          {!collapsed && (
            <div className="flex flex-col text-left">
              <span className="font-black text-lg tracking-tighter text-black leading-none">
                FINDOC
              </span>
              <span className="text-[8px] uppercase font-mono tracking-[0.16em] text-neutral-500 mt-1">
                INTELLIGENCE
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-7 w-7 items-center justify-center border border-black bg-white text-black hover:bg-black hover:text-white transition-colors cursor-pointer"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="h-3.5 w-3.5" />
          ) : (
            <ChevronLeft className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {!collapsed && (
          <p className="px-3 pb-2 text-[9px] font-mono font-bold uppercase tracking-[0.14em] text-neutral-400">
            [ NAVIGATION ]
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
                "group relative flex items-center gap-3 px-3 py-2 text-xs font-black uppercase tracking-wider transition-all duration-100",
                isActive
                  ? "bg-black text-white border-l-4 border-l-[#FF0000]"
                  : "text-black hover:bg-neutral-100"
              )}
              title={collapsed ? item.name : undefined}
            >
              <span
                className={cn(
                  "font-mono text-[10px] w-4",
                  isActive ? "text-[#FF0000]" : "text-neutral-400"
                )}
              >
                {item.code}
              </span>
              <Icon
                className={cn(
                  "h-4 w-4 shrink-0",
                  isActive ? "text-white" : "text-black"
                )}
              />
              {!collapsed && (
                <span className="flex-1 truncate">{item.name}</span>
              )}
              {!collapsed && item.badge && (
                <span
                  className={cn(
                    "text-[8px] font-mono font-bold px-1 py-0.5 border",
                    isActive
                      ? "border-[#FF0000] text-[#FF0000]"
                      : "border-black text-black"
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
        <div className="p-3 border-t border-black">
          <div className="border border-black p-3 bg-neutral-50 text-xs">
            <div className="flex items-center justify-between text-black font-black uppercase tracking-wider text-[10px] mb-1">
              <span>SYSTEM ONLINE</span>
              <span className="h-2 w-2 rounded-full bg-[#FF0000] animate-pulse" />
            </div>
            <p className="text-[10px] font-mono text-neutral-600 leading-tight">
              Pgvector • HNSW Ind AS 116 Compliant
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
