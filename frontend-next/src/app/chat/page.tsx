"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, Sparkles, Send, FileText, Info } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  const { activeDocument } = useWorkspaceStore();

  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bot className="h-5 w-5 text-cyan-400" />
            AI Financial Analyst
          </h2>
          <p className="text-sm text-slate-400">
            {activeDocument
              ? `Context: ${activeDocument.company_name || activeDocument.filename} (FY${activeDocument.fiscal_year || "—"})`
              : "Select a document in the top bar to chat with the AI Analyst."}
          </p>
        </div>
      </div>

      <Card className="flex flex-col h-[calc(100vh-210px)] border-slate-800 bg-slate-900/50">
        <CardHeader className="border-b border-slate-800/80 py-3 px-6 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span>RAG Query Engine • Citations & Page References</span>
          </div>
          {activeDocument && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-300 truncate max-w-[200px]">
              {activeDocument.company_name || activeDocument.filename}
            </span>
          )}
        </CardHeader>

        {/* Message Thread Area */}
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="flex gap-3 max-w-2xl bg-slate-950/60 p-4 rounded-xl border border-slate-800">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shrink-0 text-white font-bold text-xs">
              AI
            </div>
            <div className="space-y-1 text-sm">
              <p className="font-semibold text-white">FinDoc AI Assistant</p>
              <p className="text-slate-300 text-xs leading-relaxed">
                Hello! I am your AI Financial Analyst. You can ask me questions regarding revenue drivers, EBITDA margin trends, debt obligations, Ind AS compliance notes, or executive risks for the selected filing.
              </p>
            </div>
          </div>
        </CardContent>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <Input
              placeholder={
                activeDocument
                  ? `Ask a question about ${activeDocument.company_name || "this filing"}...`
                  : "Please select an active filing above to ask questions..."
              }
              disabled={!activeDocument}
              className="bg-slate-900/90 border-slate-700"
            />
            <Button
              variant="gradient"
              disabled={!activeDocument}
              className="gap-2 shrink-0"
            >
              <Send className="h-4 w-4" />
              <span>Ask</span>
            </Button>
          </div>
        </div>
      </Card>
    </AppLayout>
  );
}
