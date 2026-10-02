"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadDropzone } from "@/components/documents/upload-dropzone";
import { MetadataForm } from "@/components/documents/metadata-form";
import { IngestionStepper } from "@/components/documents/ingestion-stepper";
import { DocumentTable } from "@/components/documents/document-table";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { FolderUp, Sparkles, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DocumentsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeUploadId, setActiveUploadId] = useState<string | null>(null);
  const [activeUploadFilename, setActiveUploadFilename] = useState<string>("");
  const [uploadError, setUploadError] = useState<string | null>(null);

  const queryClient = useQueryClient();
  const { setActiveDocument } = useWorkspaceStore();

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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <FolderUp className="h-5 w-5 text-blue-400" />
            Document Ingestion & Index Management
          </h2>
          <p className="text-sm text-slate-400">
            Upload financial filings for automated text extraction, vector embedding, and Ind AS metric synthesis.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          className="gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Live Ingestion Stepper Banner (shown during or right after upload) */}
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
      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            Upload New Filing
          </CardTitle>
          <CardDescription>
            Select a PDF document and optionally provide filing metadata for enriched financial indexing.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <UploadDropzone
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
            disabled={uploadMutation.isPending}
          />

          {selectedFile && (
            <div className="pt-2 border-t border-slate-800">
              <MetadataForm
                selectedFile={selectedFile}
                onSubmit={handleMetadataSubmit}
                isLoading={uploadMutation.isPending}
              />
            </div>
          )}

          {uploadError && (
            <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document Catalog */}
      <Card className="border-slate-800 bg-slate-900/40">
        <CardHeader>
          <CardTitle className="text-base">
            Indexed Filings ({documents.length})
          </CardTitle>
          <CardDescription>
            Manage ingested documents, set active analytics workspace, or inspect extraction status.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DocumentTable
            documents={documents}
            isLoading={isLoading}
            onDelete={handleDeleteDocument}
            onRefresh={() => refetch()}
          />
        </CardContent>
      </Card>
    </AppLayout>
  );
}
