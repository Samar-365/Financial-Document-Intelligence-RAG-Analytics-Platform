"use client";

import React from "react";
import { Sparkles, TrendingUp, AlertTriangle, ShieldCheck, PieChart, FileText } from "lucide-react";

interface SuggestedInquiriesProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

const INQUIRIES = [
  {
    text: "What was the total revenue?",
    icon: TrendingUp,
    badge: "Revenue",
  },
  {
    text: "What is the operating margin?",
    icon: PieChart,
    badge: "Profitability",
  },
  {
    text: "What were the major risks?",
    icon: AlertTriangle,
    badge: "Risk",
  },
  {
    text: "How much debt does the company have?",
    icon: ShieldCheck,
    badge: "Leverage",
  },
  {
    text: "How did revenue change YoY?",
    icon: TrendingUp,
    badge: "Growth",
  },
  {
    text: "Summarize the financial highlights.",
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
      <div className="flex items-center gap-1.5 text-xs text-[#CBD5E1] font-semibold">
        <Sparkles className="h-3.5 w-3.5 text-[#E63946]" />
        <span>Suggested Inquiries</span>
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
              className="flex items-center gap-2.5 p-2.5 text-left rounded-xl border border-[rgba(196,30,58,0.3)] bg-[#111017] hover:bg-[rgba(184,29,36,0.18)] hover:border-[#E63946] hover:shadow-[0_0_12px_rgba(230,57,70,0.25)] text-xs text-[#CBD5E1] hover:text-white transition-all disabled:opacity-50 disabled:pointer-events-none group cursor-pointer"
            >
              <div className="h-7 w-7 rounded-lg bg-[rgba(184,29,36,0.15)] border border-[rgba(230,57,70,0.3)] flex items-center justify-center shrink-0 text-[#E63946] group-hover:scale-105 transition-transform">
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-[10px] uppercase font-bold text-[#FFA8B2] block tracking-wider">
                  {item.badge}
                </span>
                <p className="truncate font-semibold text-slate-200 group-hover:text-white">
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
