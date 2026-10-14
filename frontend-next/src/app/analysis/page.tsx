"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { financialService } from "@/lib/services/financial-service";
import { UnitCurrencyControls } from "@/components/analysis/unit-currency-controls";
import { StatementTabs } from "@/components/analysis/statement-tabs";
import { RatioGrid } from "@/components/analysis/ratio-grid";
import { MetricsTable } from "@/components/analysis/metrics-table";
import { SourceChunkDrawer } from "@/components/analysis/source-chunk-drawer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  FileText,
  BarChart3,
  TableProperties,
  FolderUp,
  TrendingUp,
  Database,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { FinancialMetricItem } from "@/types/financial";

export default function AnalysisPage() {
  const { activeDocument, activeDocumentId, currency, unit } = useWorkspaceStore();
  const [selectedMetric, setSelectedMetric] = useState<FinancialMetricItem | null>(null);

  const currencySymbol = currency === "INR" ? "₹" : "$";

  // ── API Queries ──────────────────────────────────────────────────────────
  const {
    data: metricsData,
    isLoading: metricsLoading,
    isError: metricsError,
  } = useQuery({
    queryKey: ["financialMetrics", activeDocumentId],
    queryFn: () => financialService.getMetrics(activeDocumentId!),
    enabled: !!activeDocumentId,
    staleTime: 1000 * 60 * 5,
  });

  const {
    data: ratiosData,
    isLoading: ratiosLoading,
  } = useQuery({
    queryKey: ["financialRatios", activeDocumentId],
    queryFn: () => financialService.getRatios(activeDocumentId!),
    enabled: !!activeDocumentId,
    staleTime: 1000 * 60 * 5,
  });

  const metrics: FinancialMetricItem[] = metricsData?.metrics ?? [];

  // ── Empty state ──────────────────────────────────────────────────────────
  if (!activeDocument) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
          <div className="relative">
            <div className="h-24 w-24 rounded-2xl bg-[rgba(184,29,36,0.15)] border border-[rgba(196,30,58,0.35)] flex items-center justify-center shadow-[0_0_25px_rgba(184,29,36,0.2)]">
              <FileText className="h-12 w-12 text-[#E63946]" />
            </div>
            <div className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-[rgba(184,29,36,0.3)] border border-[rgba(230,57,70,0.6)] flex items-center justify-center">
              <span className="text-[#FF6B6B] text-xs font-bold">!</span>
            </div>
          </div>
          <div className="text-center max-w-md">
            <h2 className="text-xl font-bold text-white mb-2">No Filing Selected</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Select a processed financial filing from the workspace selector, or upload
              a new annual report to start deep-dive statement analysis.
            </p>
          </div>
          <Link href="/documents">
            <Button variant="outline" size="sm" className="gap-2 border-[rgba(196,30,58,0.35)] bg-[#111017] hover:border-[#E63946]">
              <FolderUp className="h-4 w-4 text-[#E63946]" />
              Upload Filing
            </Button>
          </Link>
        </div>
      </AppLayout>
    );
  }

  // ── Error state ──────────────────────────────────────────────────────────
  if (metricsError) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
          <p className="text-sm text-[#FF6B6B]">
            Failed to load financial metrics. Check that the backend is reachable.
          </p>
          <Link href="/documents">
            <Button variant="outline" size="sm">Go to Documents</Button>
          </Link>
        </div>
      </AppLayout>
    );
  }

  return (
    <>
      <AppLayout>
        {/* ── Hero Banner ── */}
        <div className="relative overflow-hidden rounded-2xl border border-[rgba(196,30,58,0.28)] bg-[#111017] p-6 backdrop-blur-xl shadow-2xl">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-16 -right-16 h-64 w-64 rounded-full bg-[rgba(184,29,36,0.12)] blur-3xl" />
            <div className="absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-[rgba(184,29,36,0.08)] blur-2xl" />
          </div>
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-[#E63946] mb-1">
                <Zap className="h-4 w-4 text-[#E63946] animate-pulse" />
                <span>FINANCIAL STATEMENT ANALYSIS</span>
              </div>
              <h2 className="text-2xl font-bold tracking-tight text-white">
                {activeDocument.company_name ?? "Financial Statement Deep-Dive"}
              </h2>
              <div className="text-sm text-slate-400 mt-1 flex flex-wrap items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-[#E63946]" />
                  <code className="text-slate-300 text-xs bg-[#14131D] px-2 py-0.5 rounded border border-[rgba(196,30,58,0.25)]">
                    {activeDocument.filename}
                  </code>
                </span>
                {activeDocument.fiscal_year && (
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <TrendingUp className="h-3.5 w-3.5 text-[#E63946]" />
                    <span>FY{activeDocument.fiscal_year}</span>
                  </span>
                )}
                {activeDocument.fiscal_period && (
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <Database className="h-3.5 w-3.5 text-[#E63946]" />
                    <span>{activeDocument.fiscal_period}</span>
                  </span>
                )}
              </div>
            </div>
            <UnitCurrencyControls />
          </div>
        </div>

        {/* ── Section 1: Financial Statements (Tabs) ── */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <TableProperties className="h-4 w-4 text-[#E63946]" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Financial Statements
            </h3>
            {!metricsLoading && (
              <span className="ml-auto text-xs text-slate-500">
                {metrics.length} line items extracted
                <span
                  className="ml-2 text-slate-500 text-[10px] cursor-help"
                  title="Click any row to inspect its extraction source and confidence score."
                >
                  (click a row to inspect source)
                </span>
              </span>
            )}
          </div>
          <StatementTabs
            metrics={metrics}
            currencySymbol={currencySymbol}
            unit={unit}
            isLoading={metricsLoading}
            onChunkClick={setSelectedMetric}
          />
        </section>

        {/* ── Section 2: Ratio Analysis Grid ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-4 w-4 text-[#E63946]" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Key Financial Ratios &amp; Benchmark Comparison
            </h3>
          </div>
          <RatioGrid ratios={ratiosData} isLoading={ratiosLoading} />
        </section>

        {/* ── Section 3: Margin Visualization ── */}
        {!ratiosLoading && ratiosData && (
          <section>
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="h-4 w-4 text-[#E63946]" />
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                Margin &amp; Returns Overview
              </h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { label: "Oper. Margin (OPM)", value: ratiosData.opm, suffix: "%", color: "text-[#E63946]" },
                { label: "Net Margin (NPM)", value: ratiosData.npm, suffix: "%", color: "text-emerald-400" },
                { label: "ROE", value: ratiosData.roe, suffix: "%", color: "text-[#FF4D6D]" },
                { label: "ROCE", value: ratiosData.roce, suffix: "%", color: "text-amber-400" },
                { label: "Current Ratio", value: ratiosData.current_ratio, suffix: "x", color: "text-slate-200" },
                { label: "Interest Coverage", value: ratiosData.interest_coverage, suffix: "x", color: "text-rose-400" },
              ].map(({ label, value, suffix, color }) => (
                <div
                  key={label}
                  className="rounded-xl border border-[rgba(196,30,58,0.24)] bg-[#111017] p-4 flex flex-col gap-1 hover:border-[rgba(230,57,70,0.45)] hover:shadow-[0_4px_16px_rgba(184,29,36,0.15)] transition-all"
                >
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-400">
                    {label}
                  </span>
                  <span className={`text-xl font-bold ${color}`}>
                    {value != null ? `${value.toFixed(2)}${suffix}` : "—"}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Section 4: All Extracted Metrics Table ── */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <Database className="h-4 w-4 text-slate-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              All Extracted Line Items
            </h3>
          </div>
          <MetricsTable
            metrics={metrics}
            currencySymbol={currencySymbol}
            unit={unit}
            isLoading={metricsLoading}
            onRowClick={setSelectedMetric}
          />
        </section>
      </AppLayout>

      {/* Source Chunk Drawer — rendered outside AppLayout to cover full viewport */}
      <SourceChunkDrawer
        metric={selectedMetric}
        onClose={() => setSelectedMetric(null)}
        currencySymbol={currencySymbol}
        unit={unit}
      />
    </>
  );
}
