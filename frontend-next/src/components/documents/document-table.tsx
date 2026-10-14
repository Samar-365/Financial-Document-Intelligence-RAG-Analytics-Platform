"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Trash2,
  Layers,
  Bot,
  LineChart,
  Check,
  Calendar,
  Filter,
  Eye,
} from "lucide-react";
import { DocumentItem } from "@/types/document";
import { formatBytes, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
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
  onRefresh,
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
    if (confirm(`Are you sure you want to delete "${name}"? This will remove all chunks and metrics.`)) {
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
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by company name or filename..."
            className="pl-9 h-9 text-xs border-[rgba(184,29,36,0.35)] bg-[#14131D] focus:border-[#E63946]"
          />
        </div>

        {/* Status Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "COMPLETED", "PROCESSING", "FAILED"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={cn(
                "px-2.5 py-1 rounded-lg text-xs font-semibold transition-all shrink-0",
                statusFilter === status
                  ? "bg-[#E63946] text-white shadow-md shadow-[rgba(230,57,70,0.35)]"
                  : "bg-[#111017] text-slate-400 hover:text-slate-200 border border-[rgba(184,29,36,0.28)] hover:border-[#E63946]"
              )}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table */}
      <Table>
        <TableHeader>
          <TableRow className="border-b border-[rgba(196,30,58,0.25)] bg-[#0D0C12]">
            <TableHead>Company & Filing</TableHead>
            <TableHead>Period</TableHead>
            <TableHead>File Size</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Ingestion Date</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-10 text-slate-400">
                <div className="flex flex-col items-center justify-center gap-2">
                  <Loader2 className="h-6 w-6 animate-spin text-[#E63946]" />
                  <span className="text-xs">Fetching indexed filings...</span>
                </div>
              </TableCell>
            </TableRow>
          ) : filteredDocuments.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-10 text-slate-500 text-xs">
                {searchQuery || statusFilter !== "ALL"
                  ? "No filings matching your active filters."
                  : "No documents indexed yet. Upload a PDF filing above."}
              </TableCell>
            </TableRow>
          ) : (
            filteredDocuments.map((doc) => {
              const isActive = activeDocumentId === doc.id;
              const isDeleting = deletingId === doc.id;

              return (
                <TableRow
                  key={doc.id}
                  className={cn(
                    "transition-colors hover:bg-[rgba(184,29,36,0.12)] border-b border-[rgba(196,30,58,0.18)]",
                    isActive && "bg-[rgba(184,29,36,0.18)] border-l-4 border-l-[#E63946]"
                  )}
                >
                  {/* Company & Filename */}
                  <TableCell className="font-medium text-slate-200">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(184,29,36,0.18)] text-[#E63946] border border-[rgba(196,30,58,0.35)] shrink-0">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="font-semibold text-white truncate max-w-[220px]">
                          {doc.company_name || "Unnamed Company"}
                        </span>
                        <span className="text-[11px] text-slate-400 truncate max-w-[220px]">
                          {doc.filename}
                        </span>
                      </div>
                    </div>
                  </TableCell>

                  {/* Fiscal Period */}
                  <TableCell className="text-xs text-slate-300">
                    {doc.fiscal_year ? (
                      <span className="font-medium">
                        FY{doc.fiscal_year}{" "}
                        <span className="text-slate-500 font-normal">
                          ({doc.fiscal_period || "Annual"})
                        </span>
                      </span>
                    ) : (
                      "—"
                    )}
                  </TableCell>

                  {/* Size */}
                  <TableCell className="text-xs text-slate-400">
                    {formatBytes(doc.file_size_bytes)}
                  </TableCell>

                  {/* Status Badge */}
                  <TableCell>
                    <Badge
                      variant={
                        doc.status === "COMPLETED"
                          ? "success"
                          : doc.status === "FAILED"
                          ? "destructive"
                          : "warning"
                      }
                    >
                      {doc.status}
                    </Badge>
                  </TableCell>

                  {/* Created At */}
                  <TableCell className="text-xs text-slate-400">
                    {new Date(doc.created_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}
                  </TableCell>

                  {/* Actions */}
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      {/* Active Workspace Button */}
                      <Button
                        variant={isActive ? "secondary" : "outline"}
                        size="sm"
                        onClick={() => setActiveDocument(doc)}
                        className={cn(
                          "text-xs h-7 px-2.5 gap-1 border-[rgba(196,30,58,0.3)]",
                          isActive && "bg-[rgba(184,29,36,0.25)] text-white border-[#E63946] shadow-[0_0_10px_rgba(230,57,70,0.3)]"
                        )}
                        title={isActive ? "Active Workspace" : "Set as Active Workspace"}
                      >
                        {isActive ? (
                          <>
                            <Check className="h-3 w-3 text-[#E63946]" />
                            <span>Active</span>
                          </>
                        ) : (
                          <span>Activate</span>
                        )}
                      </Button>

                      {/* Deep-Dive Links */}
                      {doc.status === "COMPLETED" && (
                        <>
                          <Link href="/analysis">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setActiveDocument(doc)}
                              className="h-7 w-7 text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10"
                              title="Inspect Financial Statements"
                            >
                              <LineChart className="h-3.5 w-3.5" />
                            </Button>
                          </Link>

                          <Link href="/chat">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setActiveDocument(doc)}
                              className="h-7 w-7 text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10"
                              title="Ask AI Analyst"
                            >
                              <Bot className="h-3.5 w-3.5" />
                            </Button>
                          </Link>
                        </>
                      )}

                      {/* Delete */}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(doc.id, doc.filename)}
                        disabled={isDeleting}
                        className="h-7 w-7 text-slate-400 hover:text-red-400 hover:bg-red-500/10"
                        title="Delete filing"
                      >
                        {isDeleting ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin text-red-400" />
                        ) : (
                          <Trash2 className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    </div>
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
