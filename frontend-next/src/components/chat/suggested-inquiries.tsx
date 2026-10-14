"use client";

import React from "react";
import { Sparkles, TrendingUp, AlertTriangle, ShieldCheck, PieChart, FileText } from "lucide-react";

interface SuggestedInquiriesProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

const INQUIRIES = [
  {
    text: "What was the total revenue and YoY growth?",
    icon: TrendingUp,
    badge: "Revenue",
  },
  {
    text: "What is the operating margin and net profit margin?",
    icon: PieChart,
    badge: "Profitability",
  },
  {
    text: "What are the principal risk factors disclosed?",
    icon: AlertTriangle,
    badge: "Risk",
  },
  {
    text: "Analyze the total debt and debt-to-equity ratio.",
    icon: ShieldCheck,
    badge: "Leverage",
  },
  {
    text: "How does operating cash flow compare to net income?",
    icon: TrendingUp,
    badge: "Cash Flow",
  },
  {
    text: "Summarize the financial highlights and MD&A outlook.",
    icon: FileText,
    badge: "Summary",
  },
];

export function SuggestedInquiries({
  onSelect,
  disabled = false,
}: SuggestedInquiriesProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
        <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
        <span>Suggested Inquiries for this Filing</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {INQUIRIES.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(item.text)}
              className="flex items-center gap-2.5 p-2.5 text-left rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/80 hover:border-blue-500/30 text-xs text-slate-300 hover:text-white transition-all disabled:opacity-50 disabled:pointer-events-none group"
            >
              <div className="h-7 w-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0 text-blue-400 group-hover:scale-105 transition-transform">
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                  {item.badge}
                </span>
                <p className="truncate font-medium text-slate-200 group-hover:text-white">
                  {item.text}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
