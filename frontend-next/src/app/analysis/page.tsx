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
import {
  FileText,
  BarChart3,
  TableProperties,
  FolderUp,
  TrendingUp,
  Database,
  ArrowRight,
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
        <div className="flex flex-col items-center justify-center min-h-[65vh] p-8">
          <div className="max-w-xl w-full border-2 border-black bg-white p-10 shadow-[8px_8px_0px_#000000] text-center">
            <div className="inline-block border border-black bg-black text-white px-3 py-1 text-xs font-mono font-bold tracking-widest uppercase mb-6">
              [ STATUS: NO ACTIVE CORPUS ]
            </div>
            <h2 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter text-black mb-4 leading-none">
              STATEMENTS <br />
              <span className="stroke-text-thick">UNAVAILABLE</span>
            </h2>
            <p className="text-sm font-mono text-zinc-600 mb-8 max-w-md mx-auto leading-relaxed">
              Select an ingested filing from the workspace selector or upload an annual report to inspect standardized financial statements and ratios.
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

  // ── Error state ──────────────────────────────────────────────────────────
  if (metricsError) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[40vh] p-8">
          <div className="max-w-md w-full border-2 border-black bg-white p-6 shadow-[6px_6px_0px_#FF0000] text-center space-y-4">
            <h3 className="text-xl font-black uppercase text-black">EXTRACTION ERROR</h3>
            <p className="text-xs font-mono text-zinc-600 uppercase">
              Failed to load financial metrics. Verify that backend service is active.
            </p>
            <Link href="/documents">
              <Button className="bg-black text-white rounded-none font-black uppercase text-xs">
                Back to Documents
              </Button>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <>
      <AppLayout>
        <div className="space-y-8">
          {/* ── Hero Banner ── */}
          <div className="border border-black bg-white p-6 sm:p-8 shadow-[6px_6px_0px_#000000]">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="inline-block w-2.5 h-2.5 bg-[#FF0000]" />
                  <span className="text-xs font-mono font-bold tracking-widest text-black uppercase">
                    [ 02 / STATEMENTS ] FINANCIAL STATEMENT AUDIT
                  </span>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black uppercase tracking-tighter text-black leading-none mb-3">
                  {activeDocument.company_name ?? "COMPANY"} <span className="stroke-text-thick">STATEMENTS</span>
                </h1>
                <div className="text-xs font-mono text-black flex flex-wrap items-center gap-3">
                  <span className="border border-black bg-zinc-100 px-2 py-0.5 font-bold">
                    FILE: {activeDocument.filename}
                  </span>
                  {activeDocument.fiscal_year && (
                    <span className="border border-black bg-white px-2 py-0.5 font-bold">
                      FY {activeDocument.fiscal_year}
                    </span>
                  )}
                  {activeDocument.fiscal_period && (
                    <span className="border border-black bg-white px-2 py-0.5 font-bold">
                      PERIOD: {activeDocument.fiscal_period}
                    </span>
                  )}
                  <span className="border border-black bg-black text-white px-2 py-0.5 font-bold uppercase">
                    CORPUS READY
                  </span>
                </div>
              </div>

              <UnitCurrencyControls />
            </div>
          </div>

          {/* ── Section 1: Financial Statements (Tabs) ── */}
          <section>
            <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-widest text-black">
                  [ 01 / STATEMENTS ]
                </span>
                <h2 className="text-sm font-black uppercase tracking-wider text-black">
                  STANDARDIZED GAAP / IFRS FINANCIAL STATEMENTS
                </h2>
              </div>
              {!metricsLoading && (
                <span className="text-[11px] font-mono text-zinc-600 uppercase">
                  {metrics.length} EXTRACTED LINE ITEMS (CLICK ROW TO INSPECT CHUNK)
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

          {/* ── Section 2: Margin Visualization ── */}
          {!ratiosLoading && ratiosData && (
            <section>
              <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black uppercase tracking-widest text-[#FF0000]">
                    [ 02 / MARGINS ]
                  </span>
                  <h2 className="text-sm font-black uppercase tracking-wider text-black">
                    MARGIN EXPANSION &amp; RETURN PROFILES
                  </h2>
                </div>
                <span className="text-[11px] font-mono text-zinc-600 uppercase">
                  PROFITABILITY METRICS
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {[
                  { label: "Oper. Margin (OPM)", value: ratiosData.opm, suffix: "%" },
                  { label: "Net Margin (NPM)", value: ratiosData.npm, suffix: "%" },
                  { label: "ROE", value: ratiosData.roe, suffix: "%" },
                  { label: "ROCE", value: ratiosData.roce, suffix: "%" },
                  { label: "Current Ratio", value: ratiosData.current_ratio, suffix: "x" },
                  { label: "Interest Coverage", value: ratiosData.interest_coverage, suffix: "x" },
                ].map(({ label, value, suffix }) => (
                  <div
                    key={label}
                    className="border border-black bg-white p-4 flex flex-col gap-1 shadow-[3px_3px_0px_#000000] hover:shadow-[5px_5px_0px_#000000] transition-shadow"
                  >
                    <span className="text-[10px] uppercase font-mono font-bold text-zinc-600">
                      {label}
                    </span>
                    <span className="text-2xl font-black text-black">
                      {value != null ? `${value.toFixed(2)}${suffix}` : "—"}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* ── Section 3: Ratio Analysis Grid ── */}
          <section>
            <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-widest text-black">
                  [ 03 / DIAGNOSTICS ]
                </span>
                <h2 className="text-sm font-black uppercase tracking-wider text-black">
                  FINANCIAL RATIOS &amp; BENCHMARK STATUS
                </h2>
              </div>
              <span className="text-[11px] font-mono text-zinc-600 uppercase">
                FORMULA EVALUATION
              </span>
            </div>
            <RatioGrid ratios={ratiosData} isLoading={ratiosLoading} />
          </section>

          {/* ── Section 4: All Extracted Metrics Table ── */}
          <section>
            <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-widest text-[#FF0000]">
                  [ 04 / PROVENANCE ]
                </span>
                <h2 className="text-sm font-black uppercase tracking-wider text-black">
                  ALL EXTRACTED FINANCIAL LINE ITEMS
                </h2>
              </div>
              <span className="text-[11px] font-mono text-zinc-600 uppercase">
                SEARCHABLE INVENTORY
              </span>
            </div>
            <MetricsTable
              metrics={metrics}
              currencySymbol={currencySymbol}
              unit={unit}
              isLoading={metricsLoading}
              onRowClick={setSelectedMetric}
            />
          </section>
        </div>
      </AppLayout>

      {/* Source Chunk Drawer */}
      <SourceChunkDrawer
        metric={selectedMetric}
        onClose={() => setSelectedMetric(null)}
        currencySymbol={currencySymbol}
        unit={unit}
      />
    </>
  );
}
