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
  unitLabel: string
): string | null {
  if (!metric || metric.value == null) return null;
  const name = metric.metric_name.toLowerCase();
  if (name.includes("eps") || name.includes("ratio") || name.includes("margin")) {
    // ratio / percentage – no unit label
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
  // If backend provides year-over-year data, wire it here.
  // Currently returning null until multi-year metrics are available.
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
    isError: metricsError,
  } = useQuery({
    queryKey: ["financialMetrics", activeDocumentId],
    queryFn: () => financialService.getMetrics(activeDocumentId!),
    enabled: !!activeDocumentId,
    staleTime: 1000 * 60 * 5,
  });

  const {
    data: healthData,
    isLoading: healthLoading,
    isError: healthError,
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
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
          <div className="relative">
            <div className="h-24 w-24 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <BarChart3 className="h-12 w-12 text-blue-400" />
            </div>
            <div className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
              <span className="text-amber-400 text-xs font-bold">!</span>
            </div>
          </div>
          <div className="text-center max-w-md">
            <h2 className="text-xl font-bold text-white mb-2">No Filing Selected</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Select a document from the workspace selector above, or upload a new annual
              report to unlock the Executive Financial Dashboard.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/documents">
              <Button variant="outline" size="sm" className="gap-2">
                <FolderUp className="h-4 w-4 text-blue-400" />
                Upload Filing
              </Button>
            </Link>
            <Link href="/chat">
              <Button variant="gradient" size="sm" className="gap-2">
                <Bot className="h-4 w-4" />
                Ask AI Analyst
              </Button>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  // ─── Active Document Dashboard ────────────────────────────────────────────
  return (
    <AppLayout>
      {/* ── Hero Banner ── */}
      <div className="relative overflow-hidden rounded-2xl border border-blue-500/20 bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-950/60 p-6 backdrop-blur-xl">
        {/* Animated background blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-16 -right-16 h-64 w-64 rounded-full bg-blue-600/8 blur-3xl" />
          <div className="absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-indigo-600/8 blur-2xl" />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 mb-1">
              <Zap className="h-4 w-4 text-cyan-400 animate-pulse" />
              <span>ACTIVE WORKSPACE</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              {activeDocument.company_name
                ? `${activeDocument.company_name} — Financial Intelligence`
                : "Financial Intelligence Dashboard"}
            </h2>
            <p className="text-sm text-slate-400 mt-1 flex flex-wrap gap-3">
              <span>
                📄 <code className="text-blue-400 text-xs">{activeDocument.filename}</code>
              </span>
              {activeDocument.fiscal_year && (
                <span>📅 FY{activeDocument.fiscal_year}</span>
              )}
              {activeDocument.fiscal_period && (
                <span>🗂 {activeDocument.fiscal_period}</span>
              )}
              <span className="text-emerald-400 font-semibold">
                ✓ {activeDocument.status}
              </span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/documents">
              <Button variant="outline" size="sm" className="gap-2">
                <FolderUp className="h-4 w-4 text-blue-400" />
                Upload Filing
              </Button>
            </Link>
            <Link href="/chat">
              <Button variant="gradient" size="sm" className="gap-2">
                <Bot className="h-4 w-4" />
                Ask AI Analyst
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* ── KPI Cards Row ── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="h-4 w-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Key Financial Indicators
          </h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <KpiCard
            title="Revenue"
            value={kpis?.revenue ?? null}
            icon={DollarSign}
            iconColor="text-blue-400"
            accentColor="hover:border-blue-500/40"
            isLoading={isDataLoading}
            yoyChange={deriveYoY(metrics, ["revenue"])}
            yoyLabel="YoY Growth"
          />
          <KpiCard
            title="EBITDA / EBIT"
            value={kpis?.ebitda ?? null}
            icon={Activity}
            iconColor="text-indigo-400"
            accentColor="hover:border-indigo-500/40"
            isLoading={isDataLoading}
            yoyChange={deriveYoY(metrics, ["ebitda"])}
          />
          <KpiCard
            title="Net Profit (PAT)"
            value={kpis?.netIncome ?? null}
            icon={TrendingUp}
            iconColor="text-emerald-400"
            accentColor="hover:border-emerald-500/40"
            isLoading={isDataLoading}
            yoyChange={deriveYoY(metrics, ["net income"])}
            yoyLabel="Margin Expansion"
          />
          <KpiCard
            title="Total Debt"
            value={kpis?.totalDebt ?? null}
            icon={Layers}
            iconColor="text-red-400"
            accentColor="hover:border-red-500/40"
            isLoading={isDataLoading}
          />
          <KpiCard
            title="Oper. Margin"
            value={kpis?.opm ?? null}
            icon={Percent}
            iconColor="text-cyan-400"
            accentColor="hover:border-cyan-500/40"
            isLoading={ratiosLoading}
            description="Operating Profit Margin"
          />
          <KpiCard
            title="Debt / Equity"
            value={kpis?.debtEquity ?? null}
            icon={CreditCard}
            iconColor="text-amber-400"
            accentColor="hover:border-amber-500/40"
            isLoading={ratiosLoading}
            description="Leverage Ratio"
          />
        </div>
      </section>

      {/* ── Health Gauge + Radar Row ── */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Health Gauge */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Target className="h-4 w-4 text-cyan-400" />
              5-Dimension Corporate Health Score
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-4 pb-6">
            <HealthGauge
              score={healthData?.overall_score ?? 0}
              size={200}
              isLoading={healthLoading}
            />
            {/* Dimension pills */}
            {!healthLoading && healthData && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 w-full">
                {[
                  { label: "Growth", value: healthData.growth_score, color: "text-emerald-400" },
                  { label: "Profitability", value: healthData.profitability_score, color: "text-blue-400" },
                  { label: "Liquidity", value: healthData.liquidity_score, color: "text-cyan-400" },
                  { label: "Leverage", value: healthData.leverage_score, color: "text-amber-400" },
                  { label: "Cash Flow", value: healthData.cash_flow_score, color: "text-indigo-400" },
                ].map(({ label, value, color }) => (
                  <div
                    key={label}
                    className="flex flex-col items-center rounded-lg border border-slate-800/60 bg-slate-800/30 px-3 py-2"
                  >
                    <span className="text-xs text-slate-500 uppercase tracking-wider mb-0.5">
                      {label}
                    </span>
                    <span className={`text-sm font-bold ${color}`}>
                      {value?.toFixed(0) ?? "—"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Radar Chart */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-400" />
              Financial Dimension Radar
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
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
      </section>

      {/* ── Charts Row ── */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Revenue Trend Chart (takes 2/3 width) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-blue-400" />
              Revenue, EBITDA &amp; Net Income Trend
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <RevenueTrendChart
              metrics={metrics}
              currencySymbol={currencySymbol}
              unit={unitLabel}
              isLoading={metricsLoading}
            />
          </CardContent>
        </Card>

        {/* Capital Structure Donut */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <PieChart className="h-4 w-4 text-emerald-400" />
              Capital Structure
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <CapitalDonutChart
              metrics={metrics}
              currencySymbol={currencySymbol}
              unit={unitLabel}
              isLoading={metricsLoading}
            />
          </CardContent>
        </Card>
      </section>

      {/* ── Risk Flags & Executive Insights ── */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Activity className="h-4 w-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Risk Indicators &amp; Audit Provenance
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <RiskFlagsCard
              riskFlags={healthData?.risk_flags ?? []}
              overallScore={healthData?.overall_score ?? null}
              documentName={activeDocument.filename}
              isLoading={healthLoading}
            />
          </div>

          {/* Quick Links */}
          <div className="flex flex-col gap-3">
            <Card className="p-4 flex flex-col gap-2">
              <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">
                Deep Dive
              </h4>
              <Link href="/analysis" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <BarChart3 className="h-4 w-4 text-blue-400" />
                  Financial Statements
                </Button>
              </Link>
              <Link href="/chat" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Bot className="h-4 w-4 text-cyan-400" />
                  AI Analyst / Q&amp;A
                </Button>
              </Link>
              <Link href="/compare" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Layers className="h-4 w-4 text-indigo-400" />
                  Peer Benchmarking
                </Button>
              </Link>
              <Link href="/audit" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Activity className="h-4 w-4 text-amber-400" />
                  Audit Logs
                </Button>
              </Link>
            </Card>

            {/* Ratio Summary Card */}
            {ratiosData && (
              <Card className="p-4">
                <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">
                  Key Ratios
                </h4>
                <div className="space-y-2">
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
                      <div key={label} className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">{label}</span>
                        <span className="font-semibold text-white">
                          {value!.toFixed(2)}
                          {suffix}
                        </span>
                      </div>
                    ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </section>
    </AppLayout>
  );
}
