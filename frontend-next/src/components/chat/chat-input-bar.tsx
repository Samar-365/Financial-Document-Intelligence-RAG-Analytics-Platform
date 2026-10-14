"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Send,
  Loader2,
  Trash2,
  Download,
  FileDown,
  Printer,
  Sparkles,
  Paperclip,
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
    <div className="border-t border-slate-800 bg-slate-950/80 p-4 backdrop-blur-xl">
      <div className="mx-auto max-w-4xl space-y-2.5">
        {/* Controls row */}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-[11px] text-slate-400">
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">
                Enter
              </kbd>
              <span>to send</span>
            </span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1 text-[11px] text-slate-400">
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">
                Shift + Enter
              </kbd>
              <span>for new line</span>
            </span>
          </div>

          {/* Action buttons (Clear, Export) */}
          {hasMessages && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={onExportMarkdown}
                title="Export conversation to Markdown (.md)"
                className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors text-[11px]"
              >
                <FileDown className="h-3.5 w-3.5 text-blue-400" />
                <span>Export MD</span>
              </button>

              <button
                type="button"
                onClick={onPrintReport}
                title="Print or save as PDF"
                className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors text-[11px]"
              >
                <Printer className="h-3.5 w-3.5 text-cyan-400" />
                <span>Print PDF</span>
              </button>

              <button
                type="button"
                onClick={onClearThread}
                title="Clear current conversation"
                className="flex items-center gap-1 px-2 py-1 rounded hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors text-[11px]"
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>Clear</span>
              </button>
            </div>
          )}
        </div>

        {/* Input box */}
        <div className="relative flex items-end gap-2 rounded-2xl border border-slate-800 bg-slate-900/90 p-2 shadow-2xl focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/30 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isGenerating}
            placeholder={placeholder}
            className="flex-1 max-h-40 min-h-[44px] resize-none bg-transparent px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none disabled:opacity-50"
          />

          <Button
            type="button"
            onClick={() => handleSubmit()}
            disabled={!input.trim() || isGenerating || disabled}
            variant="gradient"
            size="sm"
            className="h-10 px-4 rounded-xl shrink-0 gap-2 font-semibold shadow-lg shadow-blue-500/20"
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
