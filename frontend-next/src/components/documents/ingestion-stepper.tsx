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
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
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
  { id: "upload", label: "File Validation", icon: FileCheck, desc: "SHA-256 integrity & format check" },
  { id: "ocr", label: "Text Extraction & OCR", icon: Search, desc: "PyPDF & OCR text parsing" },
  { id: "chunk", label: "Semantic Chunking", icon: Scissors, desc: "Table-aware hierarchical split" },
  { id: "embed", label: "Vector Embeddings", icon: Cpu, desc: "1536-dim pgvector indexing" },
  { id: "metrics", label: "LLM Metric Extraction", icon: Sparkles, desc: "Ind AS ratios & KPI extraction" },
];

export function IngestionStepper({
  documentId,
  filename,
  onComplete,
  onDismiss,
}: IngestionStepperProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Poll the single document status every 2.5s
  const { data: document, isError } = useQuery({
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

  // Calculate current active step index
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
    <div className="rounded-xl border border-blue-500/30 bg-gradient-to-b from-blue-950/30 to-slate-900/60 p-6 backdrop-blur-xl shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
              Live Ingestion Pipeline
            </span>
            <Badge
              variant={
                isCompleted
                  ? "success"
                  : isFailed
                  ? "destructive"
                  : "default"
              }
            >
              {isCompleted ? "Ingestion Completed" : isFailed ? "Failed" : "Processing"}
            </Badge>
          </div>
          <h3 className="text-base font-bold text-white truncate max-w-lg">
            {filename}
          </h3>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span>Elapsed: {elapsedSeconds}s</span>
          {onDismiss && (
            <Button
              variant="outline"
              size="sm"
              onClick={onDismiss}
              className="text-xs h-7"
            >
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Main Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-400 font-medium">
          <span>Pipeline Progress</span>
          <span>{progressPercent}%</span>
        </div>
        <Progress value={progressPercent} />
      </div>

      {/* Stepper Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {PIPELINE_STEPS.map((step, idx) => {
          const stepNum = idx + 1;
          const isDone = isCompleted || activeStepIndex > stepNum;
          const isCurrent = !isCompleted && !isFailed && activeStepIndex === stepNum;
          const StepIcon = step.icon;

          return (
            <div
              key={step.id}
              className={cn(
                "flex flex-col p-3 rounded-lg border text-xs transition-all",
                isDone
                  ? "border-emerald-500/30 bg-emerald-950/20 text-emerald-300"
                  : isCurrent
                  ? "border-blue-500/50 bg-blue-950/40 text-blue-200 shadow-md shadow-blue-500/10 scale-[1.02]"
                  : "border-slate-800 bg-slate-900/40 text-slate-500"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <StepIcon
                  className={cn(
                    "h-4 w-4",
                    isDone
                      ? "text-emerald-400"
                      : isCurrent
                      ? "text-blue-400"
                      : "text-slate-500"
                  )}
                />
                {isDone ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
                ) : (
                  <span className="text-[10px] text-slate-600 font-mono">
                    #{stepNum}
                  </span>
                )}
              </div>
              <p className="font-semibold text-white">{step.label}</p>
              <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">
                {step.desc}
              </p>
            </div>
          );
        })}
      </div>

      {isFailed && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>
            {document?.error_message || "Document processing failed. Please check file format and retry."}
          </span>
        </div>
      )}
    </div>
  );
}
