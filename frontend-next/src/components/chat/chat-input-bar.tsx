"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Send,
  Loader2,
  Trash2,
  FileDown,
  Printer,
} from "lucide-react";

interface ChatInputBarProps {
  onSendMessage: (text: string) => void;
  onClearThread: () => void;
  onExportMarkdown: () => void;
  onPrintReport: () => void;
  isGenerating: boolean;
  disabled?: boolean;
  placeholder?: string;
  hasMessages: boolean;
}

export function ChatInputBar({
  onSendMessage,
  onClearThread,
  onExportMarkdown,
  onPrintReport,
  isGenerating,
  disabled = false,
  placeholder = "Ask about revenue, risks, ratios, or notes...",
  hasMessages,
}: ChatInputBarProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isGenerating || disabled) return;
    onSendMessage(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-[rgba(184,29,36,0.25)] bg-[#0D0C12]/95 p-4 backdrop-blur-xl">
      <div className="mx-auto max-w-4xl space-y-2.5">
        {/* Controls row */}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-[11px] text-[#94A3B8]">
              <kbd className="px-1.5 py-0.5 rounded bg-[#111017] border border-[rgba(196,30,58,0.3)] font-mono text-[10px] text-[#FFA8B2]">
                Enter
              </kbd>
              <span>to send</span>
            </span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1 text-[11px] text-[#94A3B8]">
              <kbd className="px-1.5 py-0.5 rounded bg-[#111017] border border-[rgba(196,30,58,0.3)] font-mono text-[10px] text-[#FFA8B2]">
                Shift + Enter
              </kbd>
              <span>for new line</span>
            </span>
          </div>

          {/* Action buttons (Clear, Export) */}
          {hasMessages && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onExportMarkdown}
                title="Export conversation to Markdown (.md)"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-[rgba(196,30,58,0.3)] bg-[#111017] hover:border-[#E63946] text-[#CBD5E1] hover:text-white transition-colors text-[11px]"
              >
                <FileDown className="h-3.5 w-3.5 text-[#E63946]" />
                <span>Export MD</span>
              </button>

              <button
                type="button"
                onClick={onPrintReport}
                title="Print or save as PDF"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-[rgba(196,30,58,0.3)] bg-[#111017] hover:border-[#E63946] text-[#CBD5E1] hover:text-white transition-colors text-[11px]"
              >
                <Printer className="h-3.5 w-3.5 text-[#E63946]" />
                <span>Print PDF</span>
              </button>

              <button
                type="button"
                onClick={onClearThread}
                title="Clear current conversation"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-[rgba(196,30,58,0.3)] bg-[#111017] hover:bg-rose-500/10 hover:border-rose-500 text-slate-400 hover:text-rose-400 transition-colors text-[11px]"
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>Clear</span>
              </button>
            </div>
          )}
        </div>

        {/* Input box */}
        <div className="relative flex items-end gap-2 rounded-2xl border border-[rgba(196,30,58,0.35)] bg-[#111017] p-2 shadow-[0_4px_20px_rgba(0,0,0,0.5)] focus-within:border-[#E63946] focus-within:ring-1 focus-within:ring-[#E63946] focus-within:shadow-[0_0_16px_rgba(230,57,70,0.3)] transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isGenerating}
            placeholder={placeholder}
            className="flex-1 max-h-40 min-h-[44px] resize-none bg-transparent px-3 py-2.5 text-sm text-[#F1F5F9] placeholder-slate-500 focus:outline-none disabled:opacity-50"
          />

          <Button
            type="button"
            onClick={() => handleSubmit()}
            disabled={!input.trim() || isGenerating || disabled}
            variant="gradient"
            size="sm"
            className="h-10 px-4 rounded-xl shrink-0 gap-2 font-bold"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-white" />
                <span className="hidden sm:inline">Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span className="hidden sm:inline">Ask AI</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
