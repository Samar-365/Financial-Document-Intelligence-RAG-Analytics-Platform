"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { ChatMessage, Citation } from "@/types/rag";
import { MarkdownRenderer } from "./markdown-renderer";
import {
  Bot,
  User,
  Clock,
  Layers,
  Copy,
  Check,
  BookOpen,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface ChatMessageItemProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
}

export function ChatMessageItem({
  message,
  onCitationClick,
}: ChatMessageItemProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formattedTime = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 max-w-3xl ml-auto">
        <div className="flex flex-col items-end space-y-1 max-w-[85%]">
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span>{formattedTime}</span>
            <span className="font-semibold text-slate-300">You</span>
          </div>
          <div className="rounded-2xl rounded-tr-sm bg-gradient-to-r from-blue-600/90 to-blue-700/90 text-white px-4 py-3 text-sm shadow-md border border-blue-500/30 leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
        <div className="h-8 w-8 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center shrink-0 text-blue-400 mt-5">
          <User className="h-4 w-4" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3.5 max-w-4xl mr-auto group">
      {/* AI Avatar */}
      <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center shrink-0 text-white shadow-lg shadow-blue-500/20 border border-blue-400/30">
        <Bot className="h-4 w-4 text-white" />
      </div>

      {/* Message Body */}
      <div className="flex-1 space-y-2.5 overflow-hidden">
        {/* Assistant Header & Telemetry */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-white flex items-center gap-1.5">
              FinDoc AI Analyst
              <Sparkles className="h-3 w-3 text-cyan-400" />
            </span>
            {message.model_used && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                {message.model_used}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3 text-[11px] text-slate-400">
            {message.latency_ms !== undefined && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 text-slate-500" />
                <span>{message.latency_ms}ms</span>
              </span>
            )}
            {message.citations && message.citations.length > 0 && (
              <span className="flex items-center gap-1">
                <Layers className="h-3 w-3 text-blue-400" />
                <span className="text-blue-300 font-medium">
                  {message.citations.length} sources
                </span>
              </span>
            )}
            <span>{formattedTime}</span>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
              title="Copy answer"
            >
              {copied ? (
                <Check className="h-3.5 w-3.5 text-emerald-400" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </button>
          </div>
        </div>

        {/* Content Box */}
        <div className="rounded-2xl rounded-tl-sm bg-slate-900/80 border border-slate-800 p-5 shadow-xl backdrop-blur-sm">
          <MarkdownRenderer
            content={message.content}
            citations={message.citations}
            onCitationClick={onCitationClick}
          />

          {/* Citations Row / Chips */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-5 pt-4 border-t border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider">
                <span className="flex items-center gap-1.5 text-slate-300 text-[11px]">
                  <BookOpen className="h-3.5 w-3.5 text-blue-400" />
                  Grounded Evidence Sources ({message.citations.length})
                </span>
                <span className="text-[10px] text-slate-500 font-normal lowercase">
                  click to inspect verbatim extract
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                {message.citations.map((cite, idx) => {
                  const pct = Math.round(cite.relevance_score * 100);
                  return (
                    <button
                      key={`cite-pill-${idx}`}
                      type="button"
                      onClick={() => onCitationClick(cite)}
                      className={cn(
                        "flex items-start justify-between gap-2 text-left p-2.5 rounded-lg border transition-all text-xs",
                        "bg-slate-950/60 border-slate-800 hover:border-blue-500/40 hover:bg-slate-800/60 group/pill"
                      )}
                    >
                      <div className="space-y-1 overflow-hidden">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-blue-300">
                            Page {cite.page_number}
                          </span>
                          <span className="text-slate-500">•</span>
                          <span className="text-[10px] font-mono text-slate-400">
                            {pct}% match
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 line-clamp-1 italic font-serif">
                          &ldquo;{cite.snippet}&rdquo;
                        </p>
                      </div>
                      <ExternalLink className="h-3.5 w-3.5 text-slate-500 group-hover/pill:text-blue-400 shrink-0 mt-0.5" />
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
