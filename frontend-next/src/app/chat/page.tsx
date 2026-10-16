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
import {
  FolderUp,
  Activity,
  ChevronDown,
  ChevronUp,
  Sparkles,
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages.length, isGenerating]);

  // Handle Query Submission
  const handleSendMessage = async (questionText: string) => {
    if (!activeDocumentId || isGenerating || !questionText.trim()) return;

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
        content: `Error querying financial intelligence engine (${errorDetail}). Verify that the backend is running and that this document has completed vector indexing.`,
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

    messages.forEach((msg) => {
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

  const handlePrintReport = () => {
    window.print();
  };

  const handleClearThread = () => {
    if (!activeDocumentId) return;
    if (confirm("Clear current conversation thread for this document?")) {
      clearThread(activeDocumentId);
    }
  };

  // Empty state if no document is selected
  if (!activeDocument) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[65vh] p-8">
          <div className="max-w-xl w-full border-2 border-black bg-white p-10 shadow-[8px_8px_0px_#000000] text-center">
            <div className="inline-block border border-black bg-black text-white px-3 py-1 text-xs font-mono font-bold tracking-widest uppercase mb-6">
              [ STATUS: NO ACTIVE CORPUS ]
            </div>
            <h2 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter text-black mb-4 leading-none">
              RAG ENGINE <br />
              <span className="stroke-text-thick">OFFLINE</span>
            </h2>
            <p className="text-sm font-mono text-zinc-600 mb-8 max-w-md mx-auto leading-relaxed">
              Select an ingested filing from the top workspace selector or upload a 10-K to initiate verified citation querying and Ind AS extraction.
            </p>
            <Link href="/documents" className="inline-block">
              <Button className="bg-black text-white hover:bg-black/90 font-black uppercase tracking-wider rounded-none border border-black shadow-[3px_3px_0px_#000000] gap-2 px-6">
                <FolderUp className="h-4 w-4 text-[#FF0000]" />
                Upload Filing
              </Button>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  const periodText = activeDocument.fiscal_period
    ? `${activeDocument.fiscal_period} FY${activeDocument.fiscal_year || ""}`
    : `FY${activeDocument.fiscal_year || "—"}`;

  return (
    <AppLayout>
      <div className="flex flex-col h-[calc(100vh-130px)] max-w-5xl mx-auto space-y-4">
        {/* Document Context Header Banner */}
        <div className="border border-black bg-white p-4 shadow-[4px_4px_0px_#000000] flex items-center justify-between gap-4 shrink-0">
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="h-9 w-9 border border-black bg-black text-white flex items-center justify-center shrink-0">
              <Activity className="h-4 w-4 text-[#FF0000]" />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-mono font-bold tracking-widest uppercase text-zinc-500">
                [ 03 / RAG ] ACTIVE ANALYTICS CONTEXT
              </div>
              <h1 className="text-base font-black uppercase text-black truncate leading-tight">
                {activeDocument.company_name || activeDocument.filename}
                <span className="text-zinc-400 mx-2 font-normal">•</span>
                <span className="text-black font-black">{periodText}</span>
                <span className="text-zinc-400 mx-2 font-normal">•</span>
                <span className="text-zinc-600 font-mono text-xs">{currency}</span>
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 border border-black bg-zinc-100 text-black text-xs font-mono max-w-[240px] truncate font-bold">
              <span className="truncate">{activeDocument.filename}</span>
            </span>

            <button
              type="button"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase text-black px-2.5 py-1 border border-black bg-white hover:bg-black hover:text-white transition-colors shadow-[1px_1px_0px_#000000]"
            >
              <Sparkles className="h-3.5 w-3.5 text-[#FF0000]" />
              <span className="hidden sm:inline">INQUIRIES</span>
              {showSuggestions ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>
          </div>
        </div>

        {/* Collapsible Suggestions Drawer */}
        {showSuggestions && (
          <div className="shrink-0 transition-all">
            <SuggestedInquiries
              onSelect={(query) => handleSendMessage(query)}
              disabled={isGenerating}
            />
          </div>
        )}

        {/* Message Thread Scroll Area */}
        <div className="flex-1 overflow-y-auto pr-1 space-y-6 pb-6">
          {!hasMessages && (
            <div className="flex flex-col items-center justify-center py-16 text-center text-black space-y-3 border border-black bg-white p-8 shadow-[4px_4px_0px_#000000]">
              <div className="h-12 w-12 border border-black bg-black text-white flex items-center justify-center">
                <Activity className="h-6 w-6 text-[#FF0000]" />
              </div>
              <div>
                <p className="text-sm font-black uppercase text-black">
                  CORPUS INDEXED: {activeDocument.company_name || activeDocument.filename}
                </p>
                <p className="text-xs font-mono text-zinc-600 max-w-sm mt-1 uppercase">
                  Select a suggested inquiry above or execute custom natural language financial queries below. All statements are grounded with verifiable page citations.
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
            <div className="flex justify-start gap-3.5 max-w-2xl mr-auto">
              <div className="h-9 w-9 border border-black bg-black text-white flex items-center justify-center shrink-0">
                <Activity className="h-4 w-4 text-[#FF0000] animate-pulse" />
              </div>
              <div className="border border-black bg-white p-4 shadow-[4px_4px_0px_#000000] flex items-center gap-3">
                <span className="inline-block w-2.5 h-2.5 bg-[#FF0000] animate-ping" />
                <span className="text-xs font-mono font-bold uppercase text-black">
                  RETRIEVING VECTOR EMBEDDINGS &amp; CITING DISCLOSURES...
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
            placeholder={`QUERY REVENUE, DEBT, RATIOS, OR RISKS IN ${activeDocument.company_name?.toUpperCase() || "THIS FILING"}...`}
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
