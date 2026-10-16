"use client";

import React, { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { financialService } from "@/lib/services/financial-service";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { HealthGauge } from "@/components/dashboard/health-gauge";
import { FinancialRadarChart } from "@/components/dashboard/financial-radar-chart";
import { RevenueTrendChart } from "@/components/dashboard/revenue-trend-chart";
import { CapitalDonutChart } from "@/components/dashboard/capital-donut-chart";
import { RiskFlagsCard } from "@/components/dashboard/risk-flags-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DollarSign,
  Activity,
  TrendingUp,
  Layers,
  BarChart3,
  PieChart,
  FolderUp,
  Bot,
  Zap,
  Target,
  Percent,
  CreditCard,
  FileText,
  Database,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { FinancialMetricItem } from "@/types/financial";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function findMetric(
  metrics: FinancialMetricItem[],
  keywords: string[]
): FinancialMetricItem | undefined {
  return metrics.find((m) =>
    keywords.some((kw) => m.metric_name.toLowerCase().includes(kw.toLowerCase()))
  );
}

function formatValue(
  metric: FinancialMetricItem | undefined,
  currencySymbol: string,
  _unitLabel: string
): string | null {
  if (!metric || metric.value == null) return null;
  const name = metric.metric_name.toLowerCase();
  if (name.includes("eps") || name.includes("ratio") || name.includes("margin")) {
    if (name.includes("ratio")) return metric.value.toFixed(2) + "x";
    if (name.includes("eps")) return `${currencySymbol}${metric.value.toFixed(2)}`;
    return metric.value.toFixed(2) + "%";
  }
  return `${currencySymbol}${metric.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}`;
}

function deriveYoY(
  _metrics: FinancialMetricItem[],
  _keywords: string[]
): number | null {
  return null;
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { activeDocument, activeDocumentId, currency, unit } = useWorkspaceStore();

  const currencySymbol = currency === "INR" ? "₹" : "$";
  const unitLabel = unit;

  // ── API Queries ──────────────────────────────────────────────────────────
  const {
    data: metricsData,
    isLoading: metricsLoading,
  } = useQuery({
    queryKey: ["financialMetrics", activeDocumentId],
    queryFn: () => financialService.getMetrics(activeDocumentId!),
    enabled: !!activeDocumentId,
    staleTime: 1000 * 60 * 5,
  });

  const {
    data: healthData,
    isLoading: healthLoading,
  } = useQuery({
    queryKey: ["healthScore", activeDocumentId],
    queryFn: () => financialService.getHealthScore(activeDocumentId!),
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
  const isDataLoading = !activeDocumentId ? false : metricsLoading || healthLoading;

  // ── KPI derivation ──────────────────────────────────────────────────────
  const kpis = useMemo(() => {
    if (!activeDocumentId) return null;
    return {
      revenue: formatValue(findMetric(metrics, ["revenue", "net sales", "total revenue"]), currencySymbol, unitLabel),
      ebitda: formatValue(findMetric(metrics, ["ebitda", "operating income", "ebit"]), currencySymbol, unitLabel),
      netIncome: formatValue(findMetric(metrics, ["net income", "net profit", "pat"]), currencySymbol, unitLabel),
      totalDebt: formatValue(findMetric(metrics, ["total debt", "borrowings", "long term debt"]), currencySymbol, unitLabel),
      eps: formatValue(findMetric(metrics, ["eps", "earnings per share"]), currencySymbol, unitLabel),
      opm: ratiosData?.opm != null ? `${ratiosData.opm.toFixed(1)}%` : null,
      npm: ratiosData?.npm != null ? `${ratiosData.npm.toFixed(1)}%` : null,
      debtEquity: ratiosData?.debt_to_equity != null ? `${ratiosData.debt_to_equity.toFixed(2)}x` : null,
    };
  }, [metrics, ratiosData, activeDocumentId, currencySymbol, unitLabel]);

  // ─── No Document Selected ────────────────────────────────────────────────
  if (!activeDocument) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[65vh] p-8">
          <div className="max-w-xl w-full border-2 border-black bg-white p-10 shadow-[8px_8px_0px_#000000] text-center">
            <div className="inline-block border border-black bg-black text-white px-3 py-1 text-xs font-mono font-bold tracking-widest uppercase mb-6">
              [ STATUS: NO ACTIVE CORPUS ]
            </div>
            <h2 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter text-black mb-4 leading-none">
              WORKSPACE <br />
              <span className="stroke-text-thick">UNINITIALIZED</span>
            </h2>
            <p className="text-sm font-mono text-zinc-600 mb-8 max-w-md mx-auto leading-relaxed">
              Select an ingested filing from the top workspace selector or upload a 10-K, 10-Q, or Annual Report to generate financial intelligence.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/documents" className="w-full sm:w-auto">
                <Button className="w-full bg-black text-white hover:bg-black/90 font-black uppercase tracking-wider rounded-none border border-black shadow-[3px_3px_0px_#000000] gap-2 px-6">
                  <FolderUp className="h-4 w-4 text-[#FF0000]" />
                  Upload Filing
                </Button>
              </Link>
              <Link href="/chat" className="w-full sm:w-auto">
                <Button variant="outline" className="w-full bg-white text-black hover:bg-black hover:text-white font-black uppercase tracking-wider rounded-none border border-black shadow-[3px_3px_0px_#000000] gap-2 px-6">
                  <Bot className="h-4 w-4" />
                  RAG Assistant
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  // ─── Active Document Dashboard ────────────────────────────────────────────
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* ── Hero Banner ── */}
        <div className="border border-black bg-white p-6 sm:p-8 shadow-[6px_6px_0px_#000000]">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-block w-2.5 h-2.5 bg-[#FF0000]" />
                <span className="text-xs font-mono font-bold tracking-widest text-black uppercase">
                  [ 00 / EXECUTIVE INTELLIGENCE ]
                </span>
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black uppercase tracking-tighter text-black leading-none mb-3">
                {activeDocument.company_name ? activeDocument.company_name : "FINANCIAL"} <span className="stroke-text-thick">INTELLIGENCE</span>
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
                  STATUS: {activeDocument.status}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <Link href="/documents">
                <Button variant="outline" size="sm" className="bg-white text-black hover:bg-black hover:text-white border border-black rounded-none font-black uppercase tracking-wider text-xs shadow-[3px_3px_0px_#000000] gap-2 px-4">
                  <FolderUp className="h-4 w-4 text-[#FF0000]" />
                  Upload
                </Button>
              </Link>
              <Link href="/chat">
                <Button size="sm" className="bg-black text-white hover:bg-black/90 border border-black rounded-none font-black uppercase tracking-wider text-xs shadow-[3px_3px_0px_#000000] gap-2 px-4">
                  <Bot className="h-4 w-4 text-[#FF0000]" />
                  Ask AI
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* ── KPI Cards Row ── */}
        <section>
          <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-widest text-black">
                [ 01 / METRICS ]
              </span>
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                Key Financial Indicators
              </h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-600 uppercase">
              STANDARDIZED GAAP / IFRS
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <KpiCard
              title="Revenue"
              value={kpis?.revenue ?? null}
              icon={DollarSign}
              isLoading={isDataLoading}
              yoyChange={deriveYoY(metrics, ["revenue"])}
              yoyLabel="YoY Growth"
            />
            <KpiCard
              title="EBITDA / EBIT"
              value={kpis?.ebitda ?? null}
              icon={Activity}
              isLoading={isDataLoading}
              yoyChange={deriveYoY(metrics, ["ebitda"])}
            />
            <KpiCard
              title="Net Profit"
              value={kpis?.netIncome ?? null}
              icon={TrendingUp}
              isLoading={isDataLoading}
              yoyChange={deriveYoY(metrics, ["net income"])}
              yoyLabel="Margin Expansion"
              description="PAT (Profit After Tax)"
            />
            <KpiCard
              title="Total Debt"
              value={kpis?.totalDebt ?? null}
              icon={Layers}
              isLoading={isDataLoading}
            />
            <KpiCard
              title="Oper. Margin"
              value={kpis?.opm ?? null}
              icon={Percent}
              isLoading={ratiosLoading}
              description="Operating Margin"
            />
            <KpiCard
              title="Debt / Equity"
              value={kpis?.debtEquity ?? null}
              icon={CreditCard}
              isLoading={ratiosLoading}
              description="Solvency Factor"
            />
          </div>
        </section>

        {/* ── Health Gauge + Radar Row ── */}
        <section>
          <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-widest text-[#FF0000]">
                [ 02 / ANALYSIS ]
              </span>
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                Corporate Solvency &amp; Dimension Radar
              </h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-600 uppercase">
              5-AXIS DIAGNOSTIC
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Health Gauge */}
            <Card className="flex flex-col border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none">
              <CardHeader className="border-b border-black pb-3">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-black flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-[#FF0000]" />
                    5-Dimension Health Index
                  </span>
                  <span className="text-[10px] font-mono font-normal text-zinc-500 uppercase">
                    SCALE: 0-100
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center gap-6 pt-6 pb-6">
                <HealthGauge
                  score={healthData?.overall_score ?? 0}
                  size={200}
                  isLoading={healthLoading}
                />
                {/* Dimension pills */}
                {!healthLoading && healthData && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 w-full">
                    {[
                      { label: "Growth", value: healthData.growth_score },
                      { label: "Profitability", value: healthData.profitability_score },
                      { label: "Liquidity", value: healthData.liquidity_score },
                      { label: "Leverage", value: healthData.leverage_score },
                      { label: "Cash Flow", value: healthData.cash_flow_score },
                    ].map(({ label, value }) => (
                      <div
                        key={label}
                        className="flex flex-col items-center border border-black bg-white px-3 py-2 shadow-[2px_2px_0px_#000000]"
                      >
                        <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest mb-0.5">
                          {label}
                        </span>
                        <span className="text-lg font-black text-black">
                          {value != null ? value.toFixed(0) : "—"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Radar Chart */}
            <Card className="flex flex-col border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none">
              <CardHeader className="border-b border-black pb-3">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-black flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-black" />
                    Financial Dimension Radar
                  </span>
                  <span className="text-[10px] font-mono font-normal text-zinc-500 uppercase">
                    POLAR PROJECTION
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 pb-4">
                <FinancialRadarChart
                  scores={{
                    growth_score: healthData?.growth_score ?? null,
                    profitability_score: healthData?.profitability_score ?? null,
                    liquidity_score: healthData?.liquidity_score ?? null,
                    leverage_score: healthData?.leverage_score ?? null,
                    cash_flow_score: healthData?.cash_flow_score ?? null,
                  }}
                  isLoading={healthLoading}
                />
              </CardContent>
            </Card>
          </div>
        </section>

        {/* ── Charts Row ── */}
        <section>
          <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-widest text-black">
                [ 03 / TRENDS ]
              </span>
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                Revenue, Earnings &amp; Capital Structure
              </h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-600 uppercase">
              BAR &amp; DONUT ANALYSIS
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Revenue Trend Chart (takes 2/3 width) */}
            <Card className="lg:col-span-2 border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none">
              <CardHeader className="border-b border-black pb-3">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-black flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-black" />
                    Revenue, EBITDA &amp; Net Income Trend
                  </span>
                  <span className="text-[10px] font-mono font-normal text-zinc-500 uppercase">
                    HISTORICAL / REPORTED
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 pb-4">
                <RevenueTrendChart
                  metrics={metrics}
                  currencySymbol={currencySymbol}
                  unit={unitLabel}
                  isLoading={metricsLoading}
                />
              </CardContent>
            </Card>

            {/* Capital Structure Donut */}
            <Card className="border border-black bg-white shadow-[4px_4px_0px_#000000] rounded-none">
              <CardHeader className="border-b border-black pb-3">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-black flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <PieChart className="h-4 w-4 text-[#FF0000]" />
                    Capital Allocation
                  </span>
                  <span className="text-[10px] font-mono font-normal text-zinc-500 uppercase">
                    EQUITY VS DEBT
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 pb-4">
                <CapitalDonutChart
                  metrics={metrics}
                  currencySymbol={currencySymbol}
                  unit={unitLabel}
                  isLoading={metricsLoading}
                />
              </CardContent>
            </Card>
          </div>
        </section>

        {/* ── Risk Flags & Executive Insights ── */}
        <section>
          <div className="flex items-center justify-between mb-4 border-b border-black pb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-widest text-[#FF0000]">
                [ 04 / GOVERNANCE ]
              </span>
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                Risk Indicators &amp; RAG Navigation
              </h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-600 uppercase">
              AUDIT PROVENANCE
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <RiskFlagsCard
                riskFlags={healthData?.risk_flags ?? []}
                overallScore={healthData?.overall_score ?? null}
                documentName={activeDocument.filename}
                isLoading={healthLoading}
              />
            </div>

            {/* Quick Links */}
            <div className="flex flex-col gap-4">
              <div className="border border-black bg-white p-5 shadow-[4px_4px_0px_#000000] rounded-none flex flex-col gap-3">
                <div className="flex items-center justify-between border-b border-black pb-2">
                  <h3 className="text-xs font-black uppercase tracking-widest text-black">
                    EXPLORE PLATFORM
                  </h3>
                  <span className="text-[10px] font-mono text-zinc-600 uppercase">DEEP DIVE</span>
                </div>
                <Link href="/analysis" className="block">
                  <Button variant="outline" size="sm" className="w-full justify-between border border-black bg-white hover:bg-black hover:text-white rounded-none font-bold uppercase tracking-wider text-xs shadow-[2px_2px_0px_#000000]">
                    <span className="flex items-center gap-2">
                      <BarChart3 className="h-4 w-4" />
                      Financial Statements
                    </span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
                <Link href="/chat" className="block">
                  <Button variant="outline" size="sm" className="w-full justify-between border border-black bg-white hover:bg-black hover:text-white rounded-none font-bold uppercase tracking-wider text-xs shadow-[2px_2px_0px_#000000]">
                    <span className="flex items-center gap-2">
                      <Bot className="h-4 w-4 text-[#FF0000]" />
                      AI Analyst / Q&amp;A
                    </span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
                <Link href="/compare" className="block">
                  <Button variant="outline" size="sm" className="w-full justify-between border border-black bg-white hover:bg-black hover:text-white rounded-none font-bold uppercase tracking-wider text-xs shadow-[2px_2px_0px_#000000]">
                    <span className="flex items-center gap-2">
                      <Layers className="h-4 w-4" />
                      Peer Benchmarking
                    </span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
                <Link href="/audit" className="block">
                  <Button variant="outline" size="sm" className="w-full justify-between border border-black bg-white hover:bg-black hover:text-white rounded-none font-bold uppercase tracking-wider text-xs shadow-[2px_2px_0px_#000000]">
                    <span className="flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Audit Logs
                    </span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>

              {/* Ratio Summary Card */}
              {ratiosData && (
                <div className="border border-black bg-white p-5 shadow-[4px_4px_0px_#000000] rounded-none">
                  <div className="flex items-center justify-between border-b border-black pb-2 mb-3">
                    <h3 className="text-xs font-black uppercase tracking-widest text-black">
                      KEY RATIOS
                    </h3>
                    <span className="text-[10px] font-mono text-zinc-600 uppercase">SUMMARY</span>
                  </div>
                  <div className="space-y-2 font-mono text-xs">
                    {[
                      { label: "OPM", value: ratiosData.opm, suffix: "%" },
                      { label: "NPM", value: ratiosData.npm, suffix: "%" },
                      { label: "ROE", value: ratiosData.roe, suffix: "%" },
                      { label: "ROCE", value: ratiosData.roce, suffix: "%" },
                      { label: "Current Ratio", value: ratiosData.current_ratio, suffix: "x" },
                      { label: "Interest Cov.", value: ratiosData.interest_coverage, suffix: "x" },
                    ]
                      .filter((r) => r.value != null)
                      .map(({ label, value, suffix }) => (
                        <div key={label} className="flex items-center justify-between border-b border-zinc-200 pb-1">
                          <span className="text-zinc-600 uppercase">{label}</span>
                          <span className="font-black text-black">
                            {value!.toFixed(2)}
                            {suffix}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
