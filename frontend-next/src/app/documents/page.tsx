"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FolderUp, FileText, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatBytes } from "@/lib/utils";

export default function DocumentsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["documents-list"],
    queryFn: () => documentService.listDocuments(1, 50),
  });

  const documents = data?.items || [];

  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            Document Ingestion & Catalog
          </h2>
          <p className="text-sm text-slate-400">
            Upload, parse, and monitor autonomous extraction pipelines for financial reports.
          </p>
        </div>
      </div>

      {/* Placeholder Upload Dropzone Box */}
      <Card className="border-dashed border-2 border-slate-700 hover:border-blue-500/60 bg-slate-900/30 transition-all cursor-pointer">
        <CardContent className="flex flex-col items-center justify-center p-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600/10 text-blue-400 mb-4 border border-blue-500/20">
            <FolderUp className="h-7 w-7" />
          </div>
          <h3 className="text-base font-semibold text-white">
            Drag and drop financial filings (PDF)
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mt-1 mb-4">
            Supports Annual Reports, 10-K, 10-Q, and Ind AS compliant financial statements up to 50MB.
          </p>
          <Button variant="gradient" size="sm">
            Select PDF File
          </Button>
        </CardContent>
      </Card>

      {/* Ingestion Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Indexed Documents ({documents.length})</CardTitle>
          <CardDescription>
            Vectorized filings available for financial intelligence & RAG querying.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Period</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Uploaded At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-6 text-slate-400">
                    Loading indexed documents...
                  </TableCell>
                </TableRow>
              ) : documents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                    No documents uploaded yet. Upload a PDF above to begin.
                  </TableCell>
                </TableRow>
              ) : (
                documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium text-slate-200 flex items-center gap-2">
                      <FileText className="h-4 w-4 text-blue-400 shrink-0" />
                      <span className="truncate max-w-[200px]">{doc.filename}</span>
                    </TableCell>
                    <TableCell>{doc.company_name || "—"}</TableCell>
                    <TableCell>
                      {doc.fiscal_year ? `FY${doc.fiscal_year}` : "—"} {doc.fiscal_period ? `(${doc.fiscal_period})` : ""}
                    </TableCell>
                    <TableCell className="text-xs text-slate-400">
                      {formatBytes(doc.file_size_bytes)}
                    </TableCell>
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
                    <TableCell className="text-xs text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </AppLayout>
  );
}
