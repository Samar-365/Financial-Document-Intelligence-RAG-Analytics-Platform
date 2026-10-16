"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function DocumentWorkspaceSync() {
  const {
    activeDocumentId,
    activeDocument,
    setActiveDocument,
  } = useWorkspaceStore();

  const { data: documentsData } = useQuery({
    queryKey: ["documents-list"],
    queryFn: () => documentService.listDocuments(1, 100),
  });

  const documents = documentsData?.items || [];

  // Auto-select first completed document if none is active
  useEffect(() => {
    if (!activeDocumentId && documents.length > 0) {
      const firstCompleted =
        documents.find((d) => d.status === "COMPLETED") || documents[0];
      setActiveDocument(firstCompleted);
    } else if (activeDocumentId && documents.length > 0) {
      const current = documents.find((d) => d.id === activeDocumentId);
      if (current && (!activeDocument || activeDocument.updated_at !== current.updated_at)) {
        setActiveDocument(current);
      }
    }
  }, [documents, activeDocumentId, activeDocument, setActiveDocument]);

  return null;
}
