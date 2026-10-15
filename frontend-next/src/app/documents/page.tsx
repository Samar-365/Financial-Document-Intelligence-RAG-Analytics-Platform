"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { UploadDropzone } from "@/components/documents/upload-dropzone";
import { MetadataForm } from "@/components/documents/metadata-form";
import { IngestionStepper } from "@/components/documents/ingestion-stepper";
import { DocumentTable } from "@/components/documents/document-table";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { FolderUp, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DocumentsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeUploadId, setActiveUploadId] = useState<string | null>(null);
  const [activeUploadFilename, setActiveUploadFilename] = useState<string>("");
  const [uploadError, setUploadError] = useState<string | null>(null);

  const queryClient = useQueryClient();

  // Query all documents
  const {
    data: documentData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["documents-list"],
    queryFn: () => documentService.listDocuments(1, 100),
    refetchInterval: activeUploadId ? 3000 : false,
  });

  const documents = documentData?.items || [];

  // Upload Mutation
  const uploadMutation = useMutation({
    mutationFn: async (metadata: {
      company_name?: string;
      fiscal_year?: number;
      fiscal_period?: string;
    }) => {
      if (!selectedFile) throw new Error("No file selected");
      return await documentService.uploadDocument({
        file: selectedFile,
        company_name: metadata.company_name,
        fiscal_year: metadata.fiscal_year,
        fiscal_period: metadata.fiscal_period,
      });
    },
    onSuccess: (res) => {
      setActiveUploadId(res.document_id);
      setActiveUploadFilename(res.filename);
      setSelectedFile(null);
      setUploadError(null);
      queryClient.invalidateQueries({ queryKey: ["documents-list"] });
    },
    onError: (err: Error) => {
      setUploadError(err.message || "Failed to upload document");
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await documentService.deleteDocument(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents-list"] });
    },
  });

  const handleMetadataSubmit = async (metadata: {
    company_name?: string;
    fiscal_year?: number;
    fiscal_period?: string;
  }) => {
    setUploadError(null);
    await uploadMutation.mutateAsync(metadata);
  };

  const handleDeleteDocument = async (id: string) => {
    await deleteMutation.mutateAsync(id);
  };

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header Banner */}
        <div className="border border-black bg-white p-6 sm:p-8 shadow-[6px_6px_0px_#000000]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-block w-2.5 h-2.5 bg-[#FF0000]" />
                <span className="text-xs font-mono font-bold tracking-widest text-black uppercase">
                  [ 01 / REPOSITORY ] INGESTION MODULE
                </span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-black uppercase tracking-tighter text-black leading-none mb-2">
                DOCUMENT <span className="stroke-text-thick">INGESTION</span>
              </h1>
              <p className="text-xs font-mono text-zinc-600 uppercase">
                VECTOR EXTRACTION &amp; CORPUS NORMALIZATION ACROSS PDF, CSV, AND SPREADSHEETS
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="border border-black bg-white hover:bg-black hover:text-white rounded-none font-black uppercase tracking-wider text-xs shadow-[3px_3px_0px_#000000] gap-2 px-4 self-start sm:self-auto"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>REFRESH</span>
            </Button>
          </div>
        </div>

        {/* Live Ingestion Stepper Banner */}
        {activeUploadId && (
          <IngestionStepper
            documentId={activeUploadId}
            filename={activeUploadFilename}
            onComplete={() => {
              queryClient.invalidateQueries({ queryKey: ["documents-list"] });
            }}
            onDismiss={() => setActiveUploadId(null)}
          />
        )}

        {/* Upload Section */}
        <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-6">
          <div className="flex items-center justify-between border-b border-black pb-3">
            <h2 className="text-sm font-black uppercase tracking-wider text-black flex items-center gap-2">
              <FolderUp className="h-4 w-4 text-[#FF0000]" />
              UPLOAD NEW CORPORATE FILING OR SPREADSHEET
            </h2>
            <span className="text-[10px] font-mono text-zinc-600 uppercase">
              LOCAL FILE INGESTION
            </span>
          </div>

          <UploadDropzone
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
            disabled={uploadMutation.isPending}
          />

          {selectedFile && (
            <div className="pt-4 border-t border-black">
              <MetadataForm
                selectedFile={selectedFile}
                onSubmit={handleMetadataSubmit}
                isLoading={uploadMutation.isPending}
              />
            </div>
          )}

          {uploadError && (
            <div className="flex items-center gap-2 border border-black bg-[#FF0000] text-white p-3 text-xs font-mono uppercase tracking-wider shadow-[3px_3px_0px_#000000]">
              <AlertCircle className="h-4 w-4 shrink-0 text-white" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Document Catalog */}
        <div className="border border-black bg-white p-6 shadow-[4px_4px_0px_#000000] space-y-4">
          <div className="flex items-center justify-between border-b border-black pb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-widest text-[#FF0000]">
                [ 02 / CATALOG ]
              </span>
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                INDEXED FILINGS ({documents.length})
              </h2>
            </div>
            <span className="text-[10px] font-mono text-zinc-600 uppercase">
              MANAGEMENT &amp; PROVENANCE
            </span>
          </div>

          <DocumentTable
            documents={documents}
            isLoading={isLoading}
            onDelete={handleDeleteDocument}
            onRefresh={() => refetch()}
          />
        </div>
      </div>
    </AppLayout>
  );
}
