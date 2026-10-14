"use client";

import React, { useState } from "react";
import { DeltaItem } from "@/types/comparison";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Download, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface DeltaTableProps {
  deltas: DeltaItem[];
  docAId: string;
  docBId: string;
  docAName: string;
  docBName: string;
  currencySymbol?: string;
  unit?: string;
}

export function DeltaTable({
  deltas,
  docAId,
  docBId,
  docAName,
  docBName,
  currencySymbol = "₹",
  unit = "Cr",
}: DeltaTableProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredDeltas = deltas.filter((d) =>
    d.metric_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTrendMeta = (metricName: string, pct: number) => {
    const isDebt = metricName.toLowerCase().includes("debt");
    if (pct === 0) {
      return {
        label: "Neutral",
        variant: "secondary" as const,
        icon: Minus,
      };
    }
    if (isDebt) {
      if (pct < 0) {
        return {
          label: "Deleveraging",
          variant: "success" as const,
          icon: TrendingDown,
        };
      }
      return {
        label: "Leverage Increase",
        variant: "destructive" as const,
        icon: TrendingUp,
      };
    }
    if (pct > 0) {
      return {
        label: "Expansion",
        variant: "success" as const,
        icon: TrendingUp,
      };
    }
    return {
      label: "Contraction",
      variant: "destructive" as const,
      icon: TrendingDown,
    };
  };

  const handleExportCSV = () => {
    if (deltas.length === 0) return;
    let csv = `Metric Name,${docAName} (Baseline),${docBName} (Target),Absolute Change,Percent Change,Variance Type\n`;
    deltas.forEach((d) => {
      const valA = d.values?.[docAId] ?? "";
      const valB = d.values?.[docBId] ?? "";
      const pct = d.percent_delta ?? 0;
      const meta = getTrendMeta(d.metric_name, pct);
      csv += `"${d.metric_name}",${valA},${valB},${d.absolute_delta ?? ""},${pct}%,${meta.label}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `findoc-delta-comparison-${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h4 className="text-sm font-bold text-white">Detailed Line-Item Variance Table</h4>
          <p className="text-xs text-slate-400">
            Absolute and percentage variance with directional financial classification
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative w-48 sm:w-60">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <Input
              placeholder="Search line item..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-8 pl-8 text-xs bg-slate-950 border-slate-800"
            />
          </div>

          <Button
            onClick={handleExportCSV}
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs border-slate-700 bg-slate-800/60 hover:bg-slate-700 text-slate-300"
          >
            <Download className="h-3.5 w-3.5 text-blue-400" />
            <span>Export CSV</span>
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/70">
        <Table>
          <TableHeader className="bg-slate-900/90 text-slate-300">
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="font-semibold text-slate-300 text-xs">
                Financial Metric
              </TableHead>
              <TableHead className="font-semibold text-blue-300 text-xs text-right">
                {docAName} (Baseline)
              </TableHead>
              <TableHead className="font-semibold text-indigo-300 text-xs text-right">
                {docBName} (Target)
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs text-right">
                Absolute Change
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs text-center">
                % Change
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs text-right">
                Variance Interpretation
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="divide-y divide-slate-800/60 font-mono text-xs">
            {filteredDeltas.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-slate-500 font-sans">
                  No matching line items found.
                </TableCell>
              </TableRow>
            ) : (
              filteredDeltas.map((d, idx) => {
                const valA = d.values?.[docAId];
                const valB = d.values?.[docBId];
                const pct = d.percent_delta ?? 0;
                const meta = getTrendMeta(d.metric_name, pct);
                const Icon = meta.icon;

                return (
                  <TableRow key={idx} className="hover:bg-slate-900/50 transition-colors">
                    <TableCell className="font-sans font-medium text-slate-200">
                      {d.metric_name}
                    </TableCell>
                    <TableCell className="text-right text-slate-300">
                      {valA !== undefined && valA !== null
                        ? `${currencySymbol}${valA.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right text-slate-200 font-semibold">
                      {valB !== undefined && valB !== null
                        ? `${currencySymbol}${valB.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right text-slate-400">
                      {d.absolute_delta !== undefined && d.absolute_delta !== null
                        ? `${d.absolute_delta > 0 ? "+" : ""}${currencySymbol}${d.absolute_delta.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold ${
                          pct > 0
                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                            : pct < 0
                            ? "bg-rose-500/15 text-rose-400 border border-rose-500/20"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {pct > 0 ? "+" : ""}
                        {pct.toFixed(2)}%
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant={meta.variant} className="gap-1 font-sans text-[10px]">
                        <Icon className="h-3 w-3" />
                        <span>{meta.label}</span>
                      </Badge>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
