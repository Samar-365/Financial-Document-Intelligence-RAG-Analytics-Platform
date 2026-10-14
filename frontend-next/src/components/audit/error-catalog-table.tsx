"use client";

import React, { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { BookOpen, Search } from "lucide-react";

const ERROR_CATALOG = [
  {
    code: "DOC_001",
    domain: "Document Processing",
    description: "File not found or inaccessible in storage path.",
    remediation: "Verify upload directory permissions and file persistence volume.",
    severity: "destructive" as const,
  },
  {
    code: "DOC_002",
    domain: "Document Processing",
    description: "Unsupported file extension or corrupted magic bytes (supported: PDF, CSV, XLSX, XLS).",
    remediation: "Upload a valid PDF (%PDF-1.x) or spreadsheet file under 50MB.",
    severity: "warning" as const,
  },
  {
    code: "DOC_003",
    domain: "Document Processing",
    description: "Payload size exceeds maximum allowed boundary of 50MB.",
    remediation: "Compress file or split into multi-part financial statements.",
    severity: "warning" as const,
  },
  {
    code: "RAG_001",
    domain: "Vector RAG",
    description: "Zero context chunks found above 0.45 similarity threshold.",
    remediation: "Rephrase query using standard financial terminology or adjust top_k.",
    severity: "secondary" as const,
  },
  {
    code: "RAG_002",
    domain: "Vector RAG",
    description: "LLM inference timeout or hybrid failover trigger.",
    remediation: "Check OpenAI API quota or ensure local Ollama daemon is running.",
    severity: "destructive" as const,
  },
  {
    code: "ANA_001",
    domain: "Financial Analytics",
    description: "Required financial line item missing for ratio formula calculation.",
    remediation: "Inspect statement tables in Source Chunk Drawer or verify Ind AS disclosures.",
    severity: "secondary" as const,
  },
  {
    code: "DB_001",
    domain: "Database",
    description: "PostgreSQL connection pool exhausted or pgvector index locked.",
    remediation: "Review max_connections pool settings in core/database.py.",
    severity: "destructive" as const,
  },
];

export function ErrorCatalogTable() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredErrors = ERROR_CATALOG.filter(
    (e) =>
      e.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-cyan-400" />
          <div>
            <h4 className="text-sm font-bold text-white">
              Platform Error & Exception Reference Catalog
            </h4>
            <p className="text-xs text-slate-400">
              Standardized error codes, fault isolation domains, and auditor remediation steps
            </p>
          </div>
        </div>

        <div className="relative w-48 sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <Input
            placeholder="Search error code or domain..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="h-8 pl-8 text-xs bg-slate-950 border-slate-800"
          />
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/70">
        <Table>
          <TableHeader className="bg-slate-900/90 text-slate-300">
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="font-semibold text-slate-300 text-xs w-28">
                Error Code
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs w-44">
                Domain
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs">
                Description & Root Cause
              </TableHead>
              <TableHead className="font-semibold text-slate-300 text-xs">
                Remediation Action
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="divide-y divide-slate-800/60 text-xs">
            {filteredErrors.map((item) => (
              <TableRow key={item.code} className="hover:bg-slate-900/40 transition-colors">
                <TableCell className="font-mono font-bold text-blue-400">
                  {item.code}
                </TableCell>
                <TableCell>
                  <span className="font-semibold text-slate-300">
                    {item.domain}
                  </span>
                </TableCell>
                <TableCell className="text-slate-300 leading-relaxed">
                  {item.description}
                </TableCell>
                <TableCell className="text-slate-400 font-mono text-[11px] leading-relaxed">
                  {item.remediation}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
