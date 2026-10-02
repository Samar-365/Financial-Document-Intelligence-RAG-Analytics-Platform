"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { GitCompare, Layers, Plus } from "lucide-react";
import Link from "next/link";

export default function ComparePage() {
  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <GitCompare className="h-5 w-5 text-indigo-400" />
            Peer Benchmarking & Comparison
          </h2>
          <p className="text-sm text-slate-400">
            Compare key financial metrics and ratio variances side-by-side across multiple companies or fiscal periods.
          </p>
        </div>

        <Button variant="outline" size="sm" className="gap-2">
          <Plus className="h-4 w-4 text-blue-400" />
          Add Company to Benchmark
        </Button>
      </div>

      <Card className="p-8 text-center bg-slate-900/40 border-slate-800">
        <div className="flex justify-center mb-3 text-slate-500">
          <Layers className="h-10 w-10 text-indigo-400/60" />
        </div>
        <h3 className="text-base font-semibold text-white">Multi-Entity Comparison Matrix</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 mb-4">
          Select 2 or more ingested documents to run automated cross-company delta calculations, margin comparisons, and variance radar overlays.
        </p>
        <Link href="/documents">
          <Button variant="gradient" size="sm">
            View Ingested Filings
          </Button>
        </Link>
      </Card>
    </AppLayout>
  );
}
