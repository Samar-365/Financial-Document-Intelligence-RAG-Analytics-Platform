"use client";

import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { documentService } from "@/lib/services/document-service";
import { financialService } from "@/lib/services/financial-service";
import { ComparisonSelector } from "@/components/compare/comparison-selector";
import { ComparativeBarChart } from "@/components/compare/comparative-bar-chart";
import { DeltaTable } from "@/components/compare/delta-table";
import { RiskProfileComparison } from "@/components/compare/risk-profile-comparison";
import { Button } from "@/components/ui/button";
import { GitCompare, Layers, FolderUp, AlertCircle } from "lucide-react";
import { DocumentItem } from "@/types/document";
import Link from "next/link";

export default function ComparePage() {
  const { activeDocumentId, currency, unit } = useWorkspaceStore();
  const currencySymbol = currency === "INR" ? "₹" : "$";

  // 1. Fetch available documents
  const {
    data: documentsData,
    isLoading: docsLoading,
  } = useQuery({
    queryKey: ["documents-list"],
    queryFn: () => documentService.listDocuments(1, 100),
  });

  const documents: DocumentItem[] = documentsData?.items || [];

  const [docAId, setDocAId] = useState<string | null>(null);
  const [docBId, setDocBId] = useState<string | null>(null);
  const [hasCompared, setHasCompared] = useState(false);

  // Initialize selected documents
  useEffect(() => {
    if (documents.length >= 2 && !docAId && !docBId) {
      if (activeDocumentId && documents.some((d: DocumentItem) => d.id === activeDocumentId)) {
        setDocAId(activeDocumentId);
        const secondDoc = documents.find((d: DocumentItem) => d.id !== activeDocumentId);
        if (secondDoc) setDocBId(secondDoc.id);
      } else {
        setDocAId(documents[0].id);
        setDocBId(documents[1].id);
      }
      setHasCompared(true);
    }
  }, [documents, activeDocumentId, docAId, docBId]);

  // 2. Fetch Comparison Deltas
  const {
    data: comparisonData,
    isLoading: comparisonLoading,
    isError: comparisonError,
    refetch: runComparison,
  } = useQuery({
    queryKey: ["comparison", docAId, docBId],
    queryFn: () => financialService.compareDocuments([docAId!, docBId!]),
    enabled: !!docAId && !!docBId && docAId !== docBId && hasCompared,
    staleTime: 1000 * 60 * 5,
  });

  // 3. Fetch Health Scores for both entities
  const { data: healthA } = useQuery({
    queryKey: ["healthScore", docAId],
    queryFn: () => financialService.getHealthScore(docAId!),
    enabled: !!docAId && hasCompared,
    staleTime: 1000 * 60 * 5,
  });

  const { data: healthB } = useQuery({
    queryKey: ["healthScore", docBId],
    queryFn: () => financialService.getHealthScore(docBId!),
    enabled: !!docBId && hasCompared,
    staleTime: 1000 * 60 * 5,
  });

  const handleSwap = () => {
    const temp = docAId;
    setDocAId(docBId);
    setDocBId(temp);
  };

  const handleCompareClick = () => {
    setHasCompared(true);
    runComparison();
  };

  const docA = documents.find((d: DocumentItem) => d.id === docAId);
  const docB = documents.find((d: DocumentItem) => d.id === docBId);
  const docAName = docA ? docA.company_name || docA.filename : "Baseline";
  const docBName = docB ? docB.company_name || docB.filename : "Target";

  const deltas = comparisonData?.deltas || [];

  return (
    <AppLayout>
      <div className="space-y-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.18)] text-[#E63946] border border-[rgba(196,30,58,0.4)] shadow-[0_0_15px_rgba(184,29,36,0.25)] shrink-0">
              <GitCompare className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white">
                Peer Benchmarking &amp; Comparison
              </h2>
              <p className="text-sm text-slate-400">
                Cross-company and multi-period variance analysis, delta calculations, and risk trajectory tracking.
              </p>
            </div>
          </div>

          <Link href="/documents">
            <Button variant="outline" size="sm" className="gap-2 border-[rgba(196,30,58,0.3)] bg-[#111017] hover:border-[#E63946] text-slate-200">
              <FolderUp className="h-4 w-4 text-[#E63946]" />
              Upload Filing
            </Button>
          </Link>
        </div>

        {/* If fewer than 2 documents exist */}
        {documents.length < 2 && !docsLoading && (
          <div className="rounded-2xl border border-[rgba(196,30,58,0.28)] bg-[#111017] p-8 text-center space-y-4 shadow-xl">
            <div className="flex justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[rgba(184,29,36,0.15)] text-[#E63946] border border-[rgba(196,30,58,0.35)] shadow-[0_0_20px_rgba(184,29,36,0.2)]">
                <Layers className="h-8 w-8" />
              </div>
            </div>
            <h3 className="text-base font-bold text-white">
              At Least Two Documents Required for Comparison
            </h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
              Currently, only {documents.length} filing is available. Please upload an additional report
              (e.g., FY2024 and FY2025, or a competitor statement) to run automated delta calculations.
            </p>
            <Link href="/documents">
              <Button variant="gradient" size="sm">
                Upload Additional Filing
              </Button>
            </Link>
          </div>
        )}

        {/* Comparison Selector */}
        {documents.length >= 2 && (
          <ComparisonSelector
            documents={documents}
            docAId={docAId}
            docBId={docBId}
            onSelectDocA={setDocAId}
            onSelectDocB={setDocBId}
            onSwap={handleSwap}
            onCompare={handleCompareClick}
            isComparing={comparisonLoading}
          />
        )}

        {/* Results Area */}
        {hasCompared && docAId && docBId && docAId !== docBId && (
          <>
            {/* Health Score & Risk Drift */}
            <RiskProfileComparison
              healthA={healthA || null}
              healthB={healthB || null}
              docAName={docAName}
              docBName={docBName}
            />

            {/* Error or Empty */}
            {comparisonError && (
              <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-300 flex items-center gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>
                  Failed to compute comparative metrics. Ensure the backend /compare endpoint is active.
                </span>
              </div>
            )}

            {/* Charts & Tables */}
            {deltas.length > 0 && (
              <>
                <ComparativeBarChart
                  deltas={deltas}
                  docAId={docAId}
                  docBId={docBId}
                  docAName={docAName}
                  docBName={docBName}
                  currencySymbol={currencySymbol}
                  unit={unit}
                />

                <DeltaTable
                  deltas={deltas}
                  docAId={docAId}
                  docBId={docBId}
                  docAName={docAName}
                  docBName={docBName}
                  currencySymbol={currencySymbol}
                  unit={unit}
                />
              </>
            )}

            {deltas.length === 0 && !comparisonLoading && !comparisonError && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-8 text-center text-slate-400 text-xs">
                No overlapping standardized financial metrics were found across these two filings to compute deltas.
              </div>
            )}
          </>
        )}
      </div>
    </AppLayout>
  );
}
