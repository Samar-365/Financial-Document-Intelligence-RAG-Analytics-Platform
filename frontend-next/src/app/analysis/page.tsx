"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, TableProperties, Layers, FileText } from "lucide-react";
import Link from "next/link";

export default function AnalysisPage() {
  const { activeDocument } = useWorkspaceStore();

  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            Financial Statement & Ratio Analysis
          </h2>
          <p className="text-sm text-slate-400">
            {activeDocument
              ? `Analyzing: ${activeDocument.company_name || activeDocument.filename} (FY${activeDocument.fiscal_year || "—"})`
              : "Select a document in the top bar to inspect its extracted financial statements."}
          </p>
        </div>
      </div>

      {!activeDocument ? (
        <Card className="p-8 text-center bg-slate-900/40 border-slate-800">
          <div className="flex justify-center mb-3 text-slate-500">
            <FileText className="h-10 w-10" />
          </div>
          <h3 className="text-base font-semibold text-white">No Filing Selected</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
            Please select a financial filing from the header selector or upload a new filing to begin deep-dive statement analysis.
          </p>
          <Link href="/documents">
            <Button variant="outline" size="sm">
              Go to Document Ingestion
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <TableProperties className="h-4 w-4 text-blue-400" />
                Income Statement (P&L)
              </CardTitle>
              <CardDescription>
                Extracted revenue breakdown, operating expenses, and margins.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 italic">
                Statement components will be fully rendered in Phase 5.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Layers className="h-4 w-4 text-emerald-400" />
                Ind AS Financial Ratios
              </CardTitle>
              <CardDescription>
                Liquidity, Solvency, Profitability & Turnover ratios computed automatically.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 italic">
                Ratios & benchmark comparison will be rendered in Phase 5.
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </AppLayout>
  );
}
