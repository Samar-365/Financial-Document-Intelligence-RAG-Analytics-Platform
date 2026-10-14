"use client";

import React, { useRef, useEffect, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { useChatStore } from "@/stores/chat-store";
import { ragService } from "@/lib/services/rag-service";
import { ChatMessageItem } from "@/components/chat/chat-message-item";
import { ChatInputBar } from "@/components/chat/chat-input-bar";
import { SuggestedInquiries } from "@/components/chat/suggested-inquiries";
import { CitationDrawer } from "@/components/chat/citation-drawer";
import { Button } from "@/components/ui/button";
import { Citation } from "@/types/rag";
import {
  Bot,
  Sparkles,
  FileText,
  FolderUp,
  Activity,
  Layers,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  const { activeDocument, activeDocumentId, currency } = useWorkspaceStore();
  const {
    threads,
    addMessage,
    clearThread,
    isGenerating,
    setIsGenerating,
    selectedCitation,
    isCitationDrawerOpen,
    openCitationDrawer,
    closeCitationDrawer,
  } = useChatStore();

  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const messages = activeDocumentId ? threads[activeDocumentId] || [] : [];
  const hasMessages = messages.length > 0;

  // Auto-scroll to bottom of conversation
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages.length, isGenerating]);

  // Handle Query Submission
  const handleSendMessage = async (questionText: string) => {
    if (!activeDocumentId || isGenerating || !questionText.trim()) return;

    // 1. Add User Message
    addMessage(activeDocumentId, {
      role: "user",
      content: questionText.trim(),
    });

    setIsGenerating(true);

    const startTime = performance.now();

    try {
      const response = await ragService.query({
        document_id: activeDocumentId,
        question: questionText.trim(),
        top_k: 5,
      });

      const elapsed = Math.round(performance.now() - startTime);

      // 2. Add Assistant Message
      addMessage(activeDocumentId, {
        role: "assistant",
        content: response.answer,
        citations: response.citations || [],
        latency_ms: response.latency_ms || elapsed,
        model_used: response.model_used || "FinDoc RAG v1",
      });
    } catch (err: unknown) {
      console.error("RAG Query Error:", err);
      const elapsed = Math.round(performance.now() - startTime);
      const errorDetail =
        err instanceof Error ? err.message : "Network error contacting query endpoint.";

      addMessage(activeDocumentId, {
        role: "assistant",
        content: `I encountered an issue querying the financial intelligence engine (${errorDetail}). Please verify that the FastAPI backend is running and that the document has been fully indexed.`,
        citations: [],
        latency_ms: elapsed,
        model_used: "Error",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // Export to Markdown file
  const handleExportMarkdown = () => {
    if (!activeDocument || messages.length === 0) return;

    const companyName = activeDocument.company_name || activeDocument.filename;
    let mdContent = `# FinDoc AI Financial Analyst Report\n\n`;
    mdContent += `**Document:** ${companyName}\n`;
    mdContent += `**Fiscal Period:** ${activeDocument.fiscal_period || "FY"} ${activeDocument.fiscal_year || ""}\n`;
    mdContent += `**Generated Date:** ${new Date().toLocaleString()}\n\n`;
    mdContent += `---\n\n`;

    messages.forEach((msg, idx) => {
      const speaker = msg.role === "user" ? "### Question" : "### AI Analyst Response";
      mdContent += `${speaker} (${new Date(msg.timestamp).toLocaleTimeString()})\n\n`;
      mdContent += `${msg.content}\n\n`;

      if (msg.citations && msg.citations.length > 0) {
        mdContent += `**Grounded Sources:**\n`;
        msg.citations.forEach((c) => {
          mdContent += `- Page ${c.page_number} (Relevance: ${(c.relevance_score * 100).toFixed(0)}%): *"${c.snippet}"*\n`;
        });
        mdContent += `\n`;
      }
      mdContent += `---\n\n`;
    });

    const blob = new Blob([mdContent], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `findoc-chat-${companyName.replace(/\s+/g, "_")}-${new Date().toISOString().slice(0, 10)}.md`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Print conversation report
  const handlePrintReport = () => {
    window.print();
  };

  // Clear current thread
  const handleClearThread = () => {
    if (!activeDocumentId) return;
    if (confirm("Are you sure you want to clear the conversation for this document?")) {
      clearThread(activeDocumentId);
    }
  };

  // Empty state if no document is selected
  if (!activeDocument) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[65vh] gap-6 text-center max-w-lg mx-auto">
          <div className="relative">
            <div className="h-24 w-24 rounded-3xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-xl shadow-blue-500/10">
              <Bot className="h-12 w-12 text-blue-400" />
            </div>
            <div className="absolute -top-1.5 -right-1.5 h-6 w-6 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
              <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold tracking-tight text-white">
              No Document Selected
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Please select a processed annual report or quarterly filing in the top bar to begin querying with verified page citations and Ind AS extraction.
            </p>
          </div>

          <Link href="/documents">
            <Button variant="gradient" className="gap-2">
              <FolderUp className="h-4 w-4" />
              Upload & Process Filing
            </Button>
          </Link>
        </div>
      </AppLayout>
    );
  }

  const periodText = activeDocument.fiscal_period
    ? `${activeDocument.fiscal_period} FY${activeDocument.fiscal_year || ""}`
    : `FY${activeDocument.fiscal_year || "—"}`;

  return (
    <AppLayout>
      <div className="flex flex-col h-[calc(100vh-130px)] max-w-5xl mx-auto">
        {/* Document Context Header Banner */}
        <div className="rounded-xl border border-[rgba(196,30,58,0.28)] bg-[#111017] p-4 mb-4 shadow-[0_4px_16px_rgba(0,0,0,0.4)] flex items-center justify-between gap-4 shrink-0">
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="h-10 w-10 rounded-lg bg-[rgba(184,29,36,0.2)] border border-[rgba(230,57,70,0.45)] flex items-center justify-center text-[#E63946] shrink-0">
              <Activity className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-bold tracking-[0.06em] uppercase text-[#94A3B8]">
                ANALYZING FILING
              </div>
              <h2 className="text-base font-bold text-white truncate leading-tight">
                {activeDocument.company_name || activeDocument.filename}
                <span className="text-slate-500 mx-2 font-normal">•</span>
                <span className="text-[#E63946] font-bold">{periodText}</span>
                <span className="text-slate-500 mx-2 font-normal">•</span>
                <span className="text-slate-300 font-mono text-xs">{currency}</span>
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="hidden md:inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[rgba(184,29,36,0.15)] border border-[rgba(184,29,36,0.3)] text-[#E63946] text-xs font-mono max-w-[240px] truncate">
              <FileText className="h-3.5 w-3.5 text-[#E63946] shrink-0" />
              <span className="truncate">{activeDocument.filename}</span>
            </span>

            <button
              type="button"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="flex items-center gap-1 text-xs text-[#CBD5E1] hover:text-white px-2.5 py-1 rounded-lg border border-[rgba(196,30,58,0.3)] bg-[#111017] hover:border-[#E63946] transition-colors"
            >
              <Sparkles className="h-3 w-3 text-[#E63946]" />
              <span className="hidden sm:inline">Inquiries</span>
              {showSuggestions ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </button>
          </div>
        </div>

        {/* Collapsible Suggestions Drawer */}
        {showSuggestions && (
          <div className="mb-4 shrink-0 transition-all">
            <SuggestedInquiries
              onSelect={(query) => handleSendMessage(query)}
              disabled={isGenerating}
            />
          </div>
        )}

        {/* Message Thread Scroll Area */}
        <div className="flex-1 overflow-y-auto pr-1 space-y-6 pb-6">
          {!hasMessages && (
            <div className="flex flex-col items-center justify-center py-12 text-center text-slate-400 space-y-3">
              <div className="h-12 w-12 rounded-2xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center text-blue-400">
                <Sparkles className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-200">
                  Ready to analyze {activeDocument.company_name || activeDocument.filename}
                </p>
                <p className="text-xs text-slate-500 max-w-sm mt-1">
                  Select an inquiry card above or type your question below. All responses are verified against page citations.
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessageItem
              key={message.id}
              message={message}
              onCitationClick={(citation) => openCitationDrawer(citation)}
            />
          ))}

          {/* Thinking / Streaming Bubble */}
          {isGenerating && (
            <div className="flex justify-start gap-3.5 max-w-2xl mr-auto animate-pulse">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center shrink-0 text-white shadow-lg">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-slate-900/90 border border-slate-800 p-4 shadow-xl flex items-center gap-3">
                <div className="flex gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-blue-400 animate-bounce" />
                  <span className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]" />
                  <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
                </div>
                <span className="text-xs text-slate-300 font-medium">
                  FinDoc AI is retrieving vector embeddings and grounding disclosures...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="shrink-0">
          <ChatInputBar
            onSendMessage={handleSendMessage}
            onClearThread={handleClearThread}
            onExportMarkdown={handleExportMarkdown}
            onPrintReport={handlePrintReport}
            isGenerating={isGenerating}
            hasMessages={hasMessages}
            placeholder={`Ask about revenue drivers, debt, risks, or margins in ${activeDocument.company_name || "this filing"}...`}
          />
        </div>

        {/* Citation Source Drawer */}
        <CitationDrawer
          citation={selectedCitation}
          isOpen={isCitationDrawerOpen}
          onClose={closeCitationDrawer}
          documentName={activeDocument.company_name || activeDocument.filename}
        />
      </div>
    </AppLayout>
  );
}
