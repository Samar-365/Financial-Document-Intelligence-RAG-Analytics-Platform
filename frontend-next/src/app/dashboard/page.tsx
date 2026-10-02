"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  ShieldCheck,
  Zap,
  ArrowUpRight,
  FolderUp,
  Bot,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { activeDocument, currency, unit } = useWorkspaceStore();

  return (
    <AppLayout>
      {/* Top Banner / Welcome Card */}
      <div className="relative overflow-hidden rounded-2xl border border-blue-500/20 bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-950/60 p-6 backdrop-blur-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 mb-1">
              <Zap className="h-4 w-4 text-cyan-400" />
              <span>ACTIVE WORKSPACE</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              {activeDocument
                ? `${activeDocument.company_name || "Company"} Financial Intelligence`
                : "Welcome to FinDoc Platform"}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              {activeDocument
                ? `Filing: ${activeDocument.filename} • FY${activeDocument.fiscal_year || "—"} (${activeDocument.fiscal_period || "Annual"})`
                : "No financial filing selected. Ingest a document or pick an existing filing above."}
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

      {/* Quick Status / Placeholder KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:border-blue-500/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Total Revenue
            </CardTitle>
            <DollarSign className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {currency === "INR" ? "₹" : "$"} 2,450.8 {unit}
            </div>
            <div className="flex items-center text-xs text-emerald-400 mt-1">
              <TrendingUp className="h-3.5 w-3.5 mr-1" />
              +14.2% YoY Growth
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-emerald-500/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Operating Margin
            </CardTitle>
            <Activity className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">21.8%</div>
            <div className="flex items-center text-xs text-emerald-400 mt-1">
              <TrendingUp className="h-3.5 w-3.5 mr-1" />
              +180 bps YoY
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-indigo-500/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Net Profit (PAT)
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-indigo-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {currency === "INR" ? "₹" : "$"} 412.3 {unit}
            </div>
            <div className="flex items-center text-xs text-emerald-400 mt-1">
              <TrendingUp className="h-3.5 w-3.5 mr-1" />
              +9.4% Margin Expansion
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-cyan-500/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Financial Health Score
            </CardTitle>
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-cyan-400">84 / 100</div>
            <div className="text-xs text-slate-400 mt-1">
              Low Risk • Strong Solvency
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="group hover:border-slate-700 transition-all">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Financial Statements</span>
              <ArrowUpRight className="h-4 w-4 text-slate-500 group-hover:text-blue-400 transition-colors" />
            </CardTitle>
            <CardDescription>
              Comprehensive P&L, Balance Sheet & Cash Flow breakdown with Ind AS compliance indicators.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/analysis">
              <Button variant="outline" size="sm" className="w-full">
                View Statements & Ratios
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="group hover:border-slate-700 transition-all">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>AI Analyst & Citations</span>
              <ArrowUpRight className="h-4 w-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            </CardTitle>
            <CardDescription>
              Conversational RAG assistant answering complex queries with verifiable page references.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/chat">
              <Button variant="outline" size="sm" className="w-full">
                Launch AI Analyst
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="group hover:border-slate-700 transition-all">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Peer Benchmarking</span>
              <ArrowUpRight className="h-4 w-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </CardTitle>
            <CardDescription>
              Side-by-side metric comparison and variance analysis across multiple companies.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/compare">
              <Button variant="outline" size="sm" className="w-full">
                Compare Filings
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
