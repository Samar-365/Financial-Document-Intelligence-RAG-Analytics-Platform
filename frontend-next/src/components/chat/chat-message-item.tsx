"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { ChatMessage, Citation } from "@/types/rag";
import { MarkdownRenderer } from "./markdown-renderer";
import {
  Activity,
  User,
  Clock,
  Layers,
  Copy,
  Check,
  BookOpen,
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
        <div className="flex flex-col items-end space-y-1.5 max-w-[85%]">
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase text-black">
            <span>{formattedTime}</span>
            <span className="bg-black text-white px-1.5 py-0.2">YOU</span>
          </div>
          <div className="border border-black bg-black text-white p-4 text-xs font-mono shadow-[3px_3px_0px_#FF0000] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
        <div className="h-8 w-8 border border-black bg-black text-white flex items-center justify-center shrink-0 mt-5">
          <User className="h-4 w-4 text-white" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3.5 max-w-4xl mr-auto group">
      {/* AI Avatar */}
      <div className="h-9 w-9 border border-black bg-white flex items-center justify-center shrink-0 shadow-[2px_2px_0px_#000000]">
        <Activity className="h-4 w-4 text-[#FF0000]" />
      </div>

      {/* Message Body */}
      <div className="flex-1 space-y-2 overflow-hidden">
        {/* Assistant Header & Telemetry */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black uppercase tracking-wider text-black flex items-center gap-1.5">
              FINANCIAL RAG ENGINE
            </span>
            <span className="text-[9px] font-mono font-bold uppercase border border-black bg-black text-white px-1.5 py-0.5">
              GROUNDED AUDIT
            </span>
            {message.model_used && (
              <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 border border-black bg-white text-black">
                {message.model_used}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3 text-[10px] font-mono text-zinc-600">
            {message.latency_ms !== undefined && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 text-black" />
                <span>{message.latency_ms}MS</span>
              </span>
            )}
            {message.citations && message.citations.length > 0 && (
              <span className="flex items-center gap-1 font-bold text-black">
                <Layers className="h-3 w-3 text-[#FF0000]" />
                <span>{message.citations.length} SOURCES</span>
              </span>
            )}
            <span>{formattedTime}</span>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="border border-black bg-white p-1 hover:bg-black hover:text-white transition-colors"
              title="Copy answer"
            >
              {copied ? (
                <Check className="h-3 w-3 text-black" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </button>
          </div>
        </div>

        {/* Content Box */}
        <div className="border border-black bg-white p-6 shadow-[5px_5px_0px_#000000]">
          <MarkdownRenderer
            content={message.content}
            citations={message.citations}
            onCitationClick={onCitationClick}
          />

          {/* Citations Row / Chips */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-6 pt-4 border-t border-black space-y-3">
              <div className="flex items-center justify-between text-xs font-mono font-bold uppercase tracking-wider text-black">
                <span className="flex items-center gap-1.5 text-xs">
                  <BookOpen className="h-3.5 w-3.5 text-[#FF0000]" />
                  GROUNDED EVIDENCE SOURCES ({message.citations.length})
                </span>
                <span className="text-[10px] text-zinc-500">
                  [ CLICK TO INSPECT CHUNK ]
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
                      className="flex items-start justify-between gap-2 text-left p-3 border border-black bg-white hover:bg-zinc-100 hover:shadow-[3px_3px_0px_#000000] transition-all group/pill cursor-pointer"
                    >
                      <div className="space-y-1 overflow-hidden">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-black uppercase text-black">
                            PAGE {cite.page_number}
                          </span>
                          <span className="text-[9px] font-mono border border-black bg-zinc-100 px-1 py-0.2 font-bold">
                            {pct}% MATCH
                          </span>
                        </div>
                        <p className="text-[11px] font-mono text-zinc-700 line-clamp-2 uppercase">
                          &ldquo;{cite.snippet}&rdquo;
                        </p>
                      </div>
                      <ExternalLink className="h-3.5 w-3.5 text-black group-hover/pill:text-[#FF0000] shrink-0 mt-0.5" />
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
