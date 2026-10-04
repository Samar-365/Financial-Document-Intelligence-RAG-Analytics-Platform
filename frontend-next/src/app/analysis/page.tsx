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
            <div className="h-24 w-24 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <FileText className="h-12 w-12 text-indigo-400" />
            </div>
            <div className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
              <span className="text-amber-400 text-xs font-bold">!</span>
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
            <Button variant="outline" size="sm" className="gap-2">
              <FolderUp className="h-4 w-4 text-blue-400" />
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
          <p className="text-sm text-red-400">
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
        <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-blue-950/30 to-slate-950/60 p-6 backdrop-blur-xl">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-16 -right-16 h-64 w-64 rounded-full bg-indigo-600/8 blur-3xl" />
            <div className="absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-blue-600/8 blur-2xl" />
          </div>
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 mb-1">
                <Zap className="h-4 w-4 text-blue-400 animate-pulse" />
                <span>FINANCIAL STATEMENT ANALYSIS</span>
              </div>
              <h2 className="text-2xl font-bold tracking-tight text-white">
                {activeDocument.company_name ?? "Financial Statement Deep-Dive"}
              </h2>
              <p className="text-sm text-slate-400 mt-1 flex flex-wrap gap-3">
                <span>
                  📄 <code className="text-indigo-400 text-xs">{activeDocument.filename}</code>
                </span>
                {activeDocument.fiscal_year && (
                  <span>📅 FY{activeDocument.fiscal_year}</span>
                )}
                {activeDocument.fiscal_period && (
                  <span>🗂 {activeDocument.fiscal_period}</span>
                )}
              </p>
            </div>
            <UnitCurrencyControls />
          </div>
        </div>

        {/* ── Section 1: Financial Statements (Tabs) ── */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <TableProperties className="h-4 w-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Financial Statements
            </h3>
            {!metricsLoading && (
              <span className="ml-auto text-xs text-slate-500">
                {metrics.length} line items extracted
                <span
                  className="ml-2 text-slate-600 text-[10px] cursor-help"
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
            <TrendingUp className="h-4 w-4 text-emerald-400" />
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
              <BarChart3 className="h-4 w-4 text-cyan-400" />
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                Margin &amp; Returns Overview
              </h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { label: "Oper. Margin (OPM)", value: ratiosData.opm, suffix: "%", color: "text-blue-400", border: "border-blue-500/20" },
                { label: "Net Margin (NPM)", value: ratiosData.npm, suffix: "%", color: "text-emerald-400", border: "border-emerald-500/20" },
                { label: "ROE", value: ratiosData.roe, suffix: "%", color: "text-indigo-400", border: "border-indigo-500/20" },
                { label: "ROCE", value: ratiosData.roce, suffix: "%", color: "text-cyan-400", border: "border-cyan-500/20" },
                { label: "Current Ratio", value: ratiosData.current_ratio, suffix: "x", color: "text-amber-400", border: "border-amber-500/20" },
                { label: "Interest Coverage", value: ratiosData.interest_coverage, suffix: "x", color: "text-rose-400", border: "border-rose-500/20" },
              ].map(({ label, value, suffix, color, border }) => (
                <div
                  key={label}
                  className={`rounded-xl border ${border} bg-slate-900/50 p-4 flex flex-col gap-1`}
                >
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
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
