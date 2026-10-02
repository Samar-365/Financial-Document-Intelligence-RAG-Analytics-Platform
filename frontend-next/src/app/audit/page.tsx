"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, Activity, Database, CheckCircle2 } from "lucide-react";

export default function AuditPage() {
  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            Audit Logs & Governance
          </h2>
          <p className="text-sm text-slate-400">
            System activity traces, extraction confidence thresholds, and vector retrieval logs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-slate-400">System Telemetry</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <span>Operational</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">PostgreSQL & pgvector active</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-slate-400">Confidence Threshold</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-blue-400">0.85 Min</div>
            <p className="text-xs text-slate-500 mt-1">LLM Extraction Filter</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs uppercase text-slate-400">Vector Embeddings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-cyan-400">1536-dim</div>
            <p className="text-xs text-slate-500 mt-1">Cosine Distance Index</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Extraction & Query Logs</CardTitle>
          <CardDescription>
            Historical records of pipeline executions and RAG queries.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Event Type</TableHead>
                <TableHead>Target Entity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Execution Time</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium text-slate-200">
                  Document Ingestion & Chunking
                </TableCell>
                <TableCell>Reliance Industries FY24</TableCell>
                <TableCell>
                  <Badge variant="success">SUCCESS</Badge>
                </TableCell>
                <TableCell className="text-xs text-slate-400">1.24s</TableCell>
                <TableCell className="text-xs text-slate-400">Just now</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium text-slate-200">
                  RAG Embedding Retrieval
                </TableCell>
                <TableCell>TCS Annual Report FY24</TableCell>
                <TableCell>
                  <Badge variant="success">SUCCESS</Badge>
                </TableCell>
                <TableCell className="text-xs text-slate-400">340ms</TableCell>
                <TableCell className="text-xs text-slate-400">5 mins ago</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </AppLayout>
  );
}
