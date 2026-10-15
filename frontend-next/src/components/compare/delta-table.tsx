"use client";

import React, { useState } from "react";
import { DeltaItem } from "@/types/comparison";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Download, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

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
        label: "NEUTRAL",
        badge: "border-black bg-white text-black",
        icon: Minus,
      };
    }
    if (isDebt) {
      if (pct < 0) {
        return {
          label: "DELEVERAGING",
          badge: "border-black bg-black text-white",
          icon: TrendingDown,
        };
      }
      return {
        label: "LEVERAGE INCREASE",
        badge: "border-black bg-[#FF0000] text-white",
        icon: TrendingUp,
      };
    }
    if (pct > 0) {
      return {
        label: "EXPANSION",
        badge: "border-black bg-black text-white",
        icon: TrendingUp,
      };
    }
    return {
      label: "CONTRACTION",
      badge: "border-black bg-[#FF0000] text-white",
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
    <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-black pb-3">
        <div>
          <h4 className="text-xs font-black uppercase tracking-wider text-black flex items-center gap-2">
            <span className="text-[#FF0000]">[ 02 / DELTAS ]</span> DETAILED LINE-ITEM VARIANCE INVENTORY
          </h4>
          <p className="text-[10px] font-mono text-zinc-600 uppercase mt-0.5">
            ABSOLUTE AND PERCENTAGE VARIANCE WITH DIRECTIONAL STATUS
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative w-48 sm:w-60">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
            <Input
              placeholder="SEARCH LINE ITEM..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-8 pl-8 text-xs font-mono uppercase rounded-none border border-black bg-white text-black placeholder:text-zinc-400 focus-visible:ring-0 focus-visible:border-black shadow-[1px_1px_0px_#000000]"
            />
          </div>

          <Button
            onClick={handleExportCSV}
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-[10px] font-mono font-bold uppercase border border-black bg-white hover:bg-black hover:text-white rounded-none shadow-[2px_2px_0px_#000000]"
          >
            <Download className="h-3.5 w-3.5" />
            <span>EXPORT CSV</span>
          </Button>
        </div>
      </div>

      <Table>
          <TableHeader className="bg-black text-white border-b-2 border-black">
            <TableRow className="bg-black text-white hover:bg-black border-b-2 border-black">
              <TableHead className="bg-black text-white font-mono font-black text-[11px] uppercase tracking-wider">
                FINANCIAL METRIC
              </TableHead>
              <TableHead className="bg-black text-white font-mono font-black text-[11px] uppercase tracking-wider text-right">
                {docAName} (BASELINE)
              </TableHead>
              <TableHead className="bg-black text-[#FF0000] font-mono font-black text-[11px] uppercase tracking-wider text-right">
                {docBName} (TARGET)
              </TableHead>
              <TableHead className="bg-black text-white font-mono font-black text-[11px] uppercase tracking-wider text-right">
                ABSOLUTE CHANGE
              </TableHead>
              <TableHead className="bg-black text-white font-mono font-black text-[11px] uppercase tracking-wider text-center">
                % CHANGE
              </TableHead>
              <TableHead className="bg-black text-white font-mono font-black text-[11px] uppercase tracking-wider text-right">
                VARIANCE INTERPRETATION
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="divide-y divide-zinc-200 font-mono text-xs">
            {filteredDeltas.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-zinc-500 uppercase">
                  NO MATCHING LINE ITEMS FOUND.
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
                  <TableRow key={idx} className="hover:bg-zinc-100 transition-colors">
                    <TableCell className="font-mono font-bold text-black uppercase">
                      {d.metric_name}
                    </TableCell>
                    <TableCell className="text-right text-black font-mono">
                      {valA !== undefined && valA !== null
                        ? `${currencySymbol}${valA.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right text-black font-black font-mono">
                      {valB !== undefined && valB !== null
                        ? `${currencySymbol}${valB.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right text-zinc-700 font-mono">
                      {d.absolute_delta !== undefined && d.absolute_delta !== null
                        ? `${d.absolute_delta > 0 ? "+" : ""}${currencySymbol}${d.absolute_delta.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit}`
                        : "—"}
                    </TableCell>
                    <TableCell className="text-center">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1 px-2 py-0.5 text-[9px] font-mono font-black uppercase border border-black",
                          pct > 0
                            ? "bg-black text-white"
                            : pct < 0
                            ? "bg-[#FF0000] text-white"
                            : "bg-zinc-100 text-black"
                        )}
                      >
                        {pct > 0 ? "+" : ""}
                        {pct.toFixed(2)}%
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={cn("inline-flex items-center gap-1 border px-2 py-0.5 text-[9px] font-mono font-black uppercase", meta.badge)}>
                        <Icon className="h-3 w-3" />
                        <span>{meta.label}</span>
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
    </div>
  );
}
