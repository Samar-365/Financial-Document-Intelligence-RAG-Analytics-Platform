"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { healthService } from "@/lib/services/health-service";
import { documentService } from "@/lib/services/document-service";
import { TelemetryCards } from "@/components/audit/telemetry-cards";
import { AuditTelemetryTable } from "@/components/audit/audit-telemetry-table";
import { ErrorCatalogTable } from "@/components/audit/error-catalog-table";
import { ShieldCheck, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AuditPage() {
  const {
    data: healthData,
    isLoading: healthLoading,
    refetch: refetchHealth,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const t0 = performance.now();
      const res = await healthService.getHealth();
      const latency = Math.round(performance.now() - t0);
      return { ...res, probeLatency: latency };
    },
    refetchInterval: 15000,
  });

  const {
    data: docsData,
    isLoading: docsLoading,
  } = useQuery({
    queryKey: ["documents-list"],
    queryFn: () => documentService.listDocuments(1, 100),
  });

  const documents = docsData?.items || [];

  return (
    <AppLayout>
      <div className="space-y-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[rgba(184,29,36,0.18)] text-[#E63946] border border-[rgba(196,30,58,0.4)] shadow-[0_0_15px_rgba(184,29,36,0.25)] shrink-0">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white">
                System Telemetry &amp; Audit Logs
              </h2>
              <p className="text-sm text-slate-400">
                Live monitoring of API health probes, pgvector database status, and processing audit logs.
              </p>
            </div>
          </div>

          <Button
            onClick={() => refetchHealth()}
            variant="outline"
            size="sm"
            className="gap-2 text-xs border-[rgba(196,30,58,0.3)] bg-[#111017] hover:bg-[rgba(184,29,36,0.15)] hover:border-[#E63946] text-slate-200"
          >
            <RefreshCw className="h-3.5 w-3.5 text-[#E63946]" />
            <span>Poll Health Probes</span>
          </Button>
        </div>

        {/* 1. Infrastructure Telemetry Probes */}
        <TelemetryCards
          health={healthData || null}
          totalDocuments={documents.length}
          latencyMs={healthData?.probeLatency}
        />

        {/* 2. Audit & Pipeline Execution Traces */}
        <AuditTelemetryTable documents={documents} />

        {/* 3. Standardized Error Catalog */}
        <ErrorCatalogTable />
      </div>
    </AppLayout>
  );
}
