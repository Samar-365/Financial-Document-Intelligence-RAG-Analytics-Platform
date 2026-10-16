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
import { FolderUp, AlertCircle } from "lucide-react";
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
  const docAName = docA ? docA.company_name || docA.filename : "BASELINE";
  const docBName = docB ? docB.company_name || docB.filename : "TARGET";

  const deltas = comparisonData?.deltas || [];

  return (
    <AppLayout>
      <div className="space-y-8 max-w-6xl mx-auto">
        {/* Header Banner */}
        <div className="border border-black bg-white p-6 sm:p-8 shadow-[6px_6px_0px_#000000]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-block w-2.5 h-2.5 bg-[#FF0000]" />
                <span className="text-xs font-mono font-bold tracking-widest text-black uppercase">
                  [ 04 / BENCHMARKING ] COMPARATIVE ANALYTICS
                </span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-black uppercase tracking-tighter text-black leading-none mb-2">
                PEER &amp; PERIOD <span className="stroke-text-thick">BENCHMARKING</span>
              </h1>
              <p className="text-xs font-mono text-zinc-600 uppercase">
                CROSS-COMPANY AND MULTI-YEAR VARIANCE ANALYSIS, DELTA MULTIPLES, AND RISK DRIFT
              </p>
            </div>

            <Link href="/documents">
              <Button
                variant="outline"
                size="sm"
                className="border border-black bg-white hover:bg-black hover:text-white rounded-none font-black uppercase tracking-wider text-xs shadow-[3px_3px_0px_#000000] gap-2 px-4"
              >
                <FolderUp className="h-3.5 w-3.5 text-[#FF0000]" />
                <span>UPLOAD</span>
              </Button>
            </Link>
          </div>
        </div>

        {/* If fewer than 2 documents exist */}
        {documents.length < 2 && !docsLoading && (
          <div className="border-2 border-black bg-white p-10 text-center space-y-4 shadow-[6px_6px_0px_#000000]">
            <div className="inline-block border border-black bg-black text-white px-3 py-1 text-xs font-mono font-bold tracking-widest uppercase">
              [ REQUIREMENT: &ge; 2 FILINGS ]
            </div>
            <h2 className="text-2xl sm:text-3xl font-black uppercase text-black">
              INSUFFICIENT FILINGS FOR COMPARISON
            </h2>
            <p className="text-xs font-mono text-zinc-600 max-w-md mx-auto leading-relaxed uppercase">
              Currently, only {documents.length} filing is indexed. Please upload an additional report
              (e.g., FY2023 vs FY2024, or a peer competitor) to compute variance deltas.
            </p>
            <div className="pt-2">
              <Link href="/documents">
                <Button className="bg-black text-white hover:bg-black/90 font-black uppercase text-xs rounded-none border border-black shadow-[3px_3px_0px_#FF0000] px-6">
                  Upload Additional Filing
                </Button>
              </Link>
            </div>
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
          <div className="space-y-8">
            {/* Health Score & Risk Drift */}
            <RiskProfileComparison
              healthA={healthA || null}
              healthB={healthB || null}
              docAName={docAName}
              docBName={docBName}
            />

            {/* Error or Empty */}
            {comparisonError && (
              <div className="border border-black bg-[#FF0000] text-white p-4 text-xs font-mono uppercase shadow-[3px_3px_0px_#000000] flex items-center gap-2">
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
              <div className="border border-black bg-white p-8 text-center text-zinc-500 text-xs font-mono uppercase shadow-[3px_3px_0px_#000000]">
                NO OVERLAPPING STANDARDIZED FINANCIAL METRICS WERE FOUND ACROSS THESE TWO FILINGS TO COMPUTE DELTAS.
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
