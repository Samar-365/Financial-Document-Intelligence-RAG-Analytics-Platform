"use client";

import React, { useEffect, useState } from "react";
import {
  FileCheck,
  Search,
  Scissors,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { cn } from "@/lib/utils";

interface IngestionStepperProps {
  documentId: string;
  filename: string;
  onComplete?: () => void;
  onDismiss?: () => void;
}

const PIPELINE_STEPS = [
  { id: "upload", label: "01. VALIDATION", desc: "SHA-256 integrity" },
  { id: "ocr", label: "02. PARSING & OCR", desc: "Text & table extract" },
  { id: "chunk", label: "03. CHUNKING", desc: "Hierarchical split" },
  { id: "embed", label: "04. VECTORIZING", desc: "pgvector embeddings" },
  { id: "metrics", label: "05. LLM RATIOS", desc: "Ind AS metric extraction" },
];

export function IngestionStepper({
  documentId,
  filename,
  onComplete,
  onDismiss,
}: IngestionStepperProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Poll the single document status every 2.5s
  const { data: document } = useQuery({
    queryKey: ["document-status", documentId],
    queryFn: () => documentService.getDocument(documentId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "COMPLETED" || status === "FAILED") return false;
      return 2500;
    },
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const status = document?.status || "PROCESSING";
  const isCompleted = status === "COMPLETED";
  const isFailed = status === "FAILED";

  useEffect(() => {
    if (isCompleted && onComplete) {
      onComplete();
    }
  }, [isCompleted, onComplete]);

  let activeStepIndex = 1;
  let progressPercent = 25;

  if (status === "UPLOADED") {
    activeStepIndex = 1;
    progressPercent = 30;
  } else if (status === "PROCESSING" || status === "PARSED") {
    activeStepIndex = 3;
    progressPercent = 65;
  } else if (status === "INDEXED") {
    activeStepIndex = 4;
    progressPercent = 85;
  } else if (isCompleted) {
    activeStepIndex = 5;
    progressPercent = 100;
  }

  return (
    <div className="border-2 border-black bg-white p-6 shadow-[6px_6px_0px_#000000] space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-black pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-block w-2.5 h-2.5 bg-[#FF0000]" />
            <span className="text-xs font-mono font-bold uppercase tracking-widest text-black">
              [ PIPELINE: INGESTION IN PROGRESS ]
            </span>
          </div>
          <h3 className="text-xl sm:text-2xl font-black uppercase tracking-tight text-black">
            PROCESSING: <span className="stroke-text-thick">{filename}</span>
          </h3>
          <p className="text-xs font-mono text-zinc-600 mt-1">
            ELAPSED TIME: {elapsedSeconds}s • TARGET: POSTGRESQL PGVECTOR
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="border border-black bg-black text-white px-3 py-1 text-xs font-mono font-bold uppercase shadow-[2px_2px_0px_#000000]">
            {status} ({progressPercent}%)
          </span>
          {onDismiss && (
            <Button
              variant="outline"
              size="sm"
              onClick={onDismiss}
              className="border border-black bg-white hover:bg-black hover:text-white rounded-none p-0 h-8 w-8 inline-flex items-center justify-center cursor-pointer"
            >
              <X size={14} strokeWidth={2} className="shrink-0" />
            </Button>
          )}
        </div>
      </div>

      {/* Minimal Progress Bar */}
      <div className="w-full h-3 border border-black bg-zinc-100 p-0.5">
        <div
          className="h-full bg-black transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Step Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {PIPELINE_STEPS.map((step, idx) => {
          const stepNum = idx + 1;
          const isDone = stepNum < activeStepIndex || isCompleted;
          const isCurrent = stepNum === activeStepIndex && !isCompleted && !isFailed;

          return (
            <div
              key={step.id}
              className={cn(
                "p-3 border transition-all",
                isCurrent
                  ? "border-2 border-black bg-zinc-100 shadow-[3px_3px_0px_#FF0000]"
                  : isDone
                  ? "border-black bg-white text-black"
                  : "border-zinc-300 bg-white opacity-40 text-zinc-400"
              )}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono font-black uppercase text-black">
                  {step.label}
                </span>
                {isCurrent && <Loader2 className="h-3 w-3 animate-spin text-[#FF0000]" />}
                {isDone && <span className="text-[10px] font-black text-black">✓</span>}
              </div>
              <p className="text-[10px] font-mono text-zinc-600 uppercase">
                {step.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
