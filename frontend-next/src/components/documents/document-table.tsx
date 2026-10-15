"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Trash2,
  Check,
  Eye,
  LineChart,
} from "lucide-react";
import { DocumentItem } from "@/types/document";
import { formatBytes, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useWorkspaceStore } from "@/stores/workspace-store";
import Link from "next/link";

interface DocumentTableProps {
  documents: DocumentItem[];
  isLoading: boolean;
  onDelete: (id: string) => Promise<void>;
  onRefresh: () => void;
}

export function DocumentTable({
  documents,
  isLoading,
  onDelete,
  onRefresh: _onRefresh,
}: DocumentTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [inspectDoc, setInspectDoc] = useState<DocumentItem | null>(null);

  const { activeDocumentId, setActiveDocument } = useWorkspaceStore();

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      (doc.company_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" || doc.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Delete filing "${name}"? This removes all vector chunks and extracted KPIs.`)) {
      setDeletingId(id);
      try {
        await onDelete(id);
        if (activeDocumentId === id) {
          setActiveDocument(null);
        }
      } finally {
        setDeletingId(null);
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls Bar: Search & Status Filters */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="FILTER BY COMPANY OR FILENAME..."
            className="pl-9 h-9 text-xs font-mono rounded-none border border-black bg-white text-black placeholder:text-zinc-400 focus-visible:ring-0 focus-visible:border-black shadow-[2px_2px_0px_#000000]"
          />
        </div>

        {/* Status Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "COMPLETED", "PROCESSING", "FAILED"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={cn(
                "px-3 py-1.5 text-[10px] font-mono font-black uppercase tracking-wider border border-black transition-all",
                statusFilter === status
                  ? "bg-black text-white shadow-[2px_2px_0px_#FF0000]"
                  : "bg-white text-black hover:bg-zinc-100"
              )}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Table Container */}
      <Table>
          <TableHeader className="bg-black text-white border-b-2 border-black">
            <TableRow className="bg-black text-white hover:bg-black border-b-2 border-black">
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider">
                DOCUMENT / FILING
              </TableHead>
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider">
                ENTITY
              </TableHead>
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider">
                PERIOD
              </TableHead>
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider">
                SIZE
              </TableHead>
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider">
                STATUS
              </TableHead>
              <TableHead className="bg-black text-white text-[11px] font-mono font-black uppercase tracking-wider text-right">
                ACTIONS
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [1, 2, 3, 4].map((i) => (
                <TableRow key={i} className="border-b border-zinc-200">
                  <TableCell colSpan={6} className="py-4">
                    <div className="h-5 bg-zinc-200 animate-pulse" />
                  </TableCell>
                </TableRow>
              ))
            ) : filteredDocuments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-12 text-center text-xs font-mono uppercase text-zinc-500">
                  NO DOCUMENTS MATCHING ACTIVE FILTER CRITERIA
                </TableCell>
              </TableRow>
            ) : (
              filteredDocuments.map((doc) => {
                const isActive = activeDocumentId === doc.id;
                return (
                  <TableRow
                    key={doc.id}
                    className={cn(
                      "border-b border-black transition-colors",
                      isActive ? "bg-zinc-100 border-l-4 border-l-[#FF0000]" : "hover:bg-zinc-50"
                    )}
                  >
                    {/* Filename & Tag */}
                    <TableCell className="py-3 font-mono text-xs">
                      <div className="flex items-center gap-2.5">
                        <FileText className={cn("h-4 w-4 shrink-0", isActive ? "text-[#FF0000]" : "text-black")} />
                        <div className="min-w-0">
                          <p className="font-bold text-black truncate max-w-[220px]">
                            {doc.filename}
                          </p>
                          <span className="text-[10px] text-zinc-500">
                            ID: {doc.id.slice(0, 8)}...
                          </span>
                        </div>
                      </div>
                    </TableCell>

                    {/* Company */}
                    <TableCell className="font-mono text-xs font-bold text-black uppercase">
                      {doc.company_name || "—"}
                    </TableCell>

                    {/* Period */}
                    <TableCell className="font-mono text-xs text-zinc-800">
                      {doc.fiscal_year ? `FY${doc.fiscal_year}` : "—"}
                      {doc.fiscal_period ? ` (${doc.fiscal_period})` : ""}
                    </TableCell>

                    {/* Size */}
                    <TableCell className="font-mono text-xs text-zinc-600">
                      {doc.file_size_bytes ? formatBytes(doc.file_size_bytes) : "—"}
                    </TableCell>

                    {/* Status Badge */}
                    <TableCell>
                      {doc.status === "COMPLETED" ? (
                        <span className="inline-flex items-center gap-1 border border-black bg-black text-white px-2 py-0.5 text-[9px] font-mono font-bold uppercase">
                          <Check className="h-3 w-3 text-white" />
                          COMPLETED
                        </span>
                      ) : doc.status === "PROCESSING" ? (
                        <span className="inline-flex items-center gap-1 border border-black bg-zinc-200 text-black px-2 py-0.5 text-[9px] font-mono font-bold uppercase">
                          <Loader2 className="h-3 w-3 animate-spin text-black" />
                          PARSING
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 border border-black bg-[#FF0000] text-white px-2 py-0.5 text-[9px] font-mono font-bold uppercase">
                          <AlertCircle className="h-3 w-3 text-white" />
                          {doc.status}
                        </span>
                      )}
                    </TableCell>

                    {/* Actions */}
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* Select as Active Document */}
                        <button
                          type="button"
                          onClick={() => setActiveDocument(doc)}
                          className={cn(
                            "h-7 px-2.5 inline-flex items-center justify-center border border-black text-[10px] font-mono font-black uppercase tracking-wider transition-colors cursor-pointer",
                            isActive
                              ? "bg-black text-white hover:bg-black/90 shadow-[1px_1px_0px_#FF0000]"
                              : "bg-white text-black hover:bg-black hover:text-white"
                          )}
                        >
                          {isActive ? "ACTIVE" : "SET ACTIVE"}
                        </button>

                        {/* Inspect Metadata */}
                        <button
                          type="button"
                          onClick={() => setInspectDoc(doc)}
                          className="h-7 w-7 p-0 inline-flex items-center justify-center border border-black bg-white hover:bg-black text-black hover:text-white transition-colors cursor-pointer"
                          title="Inspect Metadata"
                        >
                          <Eye size={14} strokeWidth={2} className="shrink-0" />
                        </button>

                        {/* Deep link to analysis */}
                        <Link
                          href="/analysis"
                          onClick={() => setActiveDocument(doc)}
                          className="h-7 w-7 p-0 inline-flex items-center justify-center border border-black bg-white hover:bg-black text-black hover:text-white transition-colors cursor-pointer"
                          title="Open Analysis"
                        >
                          <LineChart size={14} strokeWidth={2} className="shrink-0" />
                        </Link>

                        {/* Delete */}
                        <button
                          type="button"
                          disabled={deletingId === doc.id}
                          onClick={() => handleDelete(doc.id, doc.filename)}
                          className="h-7 w-7 p-0 inline-flex items-center justify-center border border-black bg-white hover:bg-[#FF0000] text-black hover:text-white transition-colors disabled:opacity-50 cursor-pointer"
                          title="Delete Filing"
                        >
                          {deletingId === doc.id ? (
                            <Loader2 size={14} strokeWidth={2} className="animate-spin shrink-0" />
                          ) : (
                            <Trash2 size={14} strokeWidth={2} className="shrink-0" />
                          )}
                        </button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

      {/* Inspect Modal Drawer */}
      {inspectDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg border-2 border-black bg-white p-6 shadow-[8px_8px_0px_#000000] space-y-4">
            <div className="flex items-center justify-between border-b border-black pb-3">
              <h3 className="text-sm font-black uppercase tracking-wider text-black flex items-center gap-2">
                <span className="text-[#FF0000]">[ METADATA ]</span> {inspectDoc.filename}
              </h3>
              <button
                onClick={() => setInspectDoc(null)}
                className="border border-black bg-black text-white px-2 py-0.5 text-xs font-mono font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">DOCUMENT ID:</span>
                <span className="text-black font-bold select-all">{inspectDoc.id}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">COMPANY:</span>
                <span className="text-black font-bold">{inspectDoc.company_name || "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">FISCAL YEAR:</span>
                <span className="text-black font-bold">{inspectDoc.fiscal_year || "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">PERIOD:</span>
                <span className="text-black font-bold">{inspectDoc.fiscal_period || "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">STATUS:</span>
                <span className="text-black font-bold">{inspectDoc.status}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-200 pb-1">
                <span className="text-zinc-600 uppercase">FILE SIZE:</span>
                <span className="text-black font-bold">{inspectDoc.file_size_bytes ? formatBytes(inspectDoc.file_size_bytes) : "N/A"}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button
                onClick={() => setInspectDoc(null)}
                className="bg-black text-white hover:bg-black/90 rounded-none border border-black font-black uppercase text-xs px-5 shadow-[2px_2px_0px_#000000]"
              >
                CLOSE
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
