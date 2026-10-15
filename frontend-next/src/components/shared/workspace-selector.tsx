"use client";

import React, { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Building2, ChevronDown } from "lucide-react";

export function WorkspaceSelector() {
  const {
    activeDocumentId,
    activeDocument,
    setActiveDocument,
    currency,
    setCurrency,
    unit,
    setUnit,
  } = useWorkspaceStore();

  const { data: documentsData, isLoading } = useQuery({
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

  const handleDocumentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = e.target.value;
    if (!selectedId) {
      setActiveDocument(null);
      return;
    }
    const found = documents.find((d) => d.id === selectedId);
    if (found) {
      setActiveDocument(found);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {/* Active Document Selector */}
      <div className="relative flex items-center">
        <div className="absolute left-2.5 pointer-events-none text-black">
          <Building2 className="h-3.5 w-3.5" />
        </div>
        <select
          value={activeDocumentId || ""}
          onChange={handleDocumentChange}
          disabled={isLoading || documents.length === 0}
          className="h-8 pl-8 pr-7 bg-white hover:bg-neutral-50 border border-black rounded-none text-xs font-mono font-bold text-black appearance-none focus:outline-none focus:ring-1 focus:ring-black cursor-pointer min-w-[190px] max-w-[270px] truncate transition-all"
        >
          {isLoading ? (
            <option value="">Loading filings...</option>
          ) : documents.length === 0 ? (
            <option value="">No filings uploaded</option>
          ) : (
            documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.company_name || "Document"}{" "}
                {doc.fiscal_year ? `(FY${doc.fiscal_year})` : ""} - {doc.filename}
              </option>
            ))
          )}
        </select>
        <ChevronDown className="absolute right-2 h-3.5 w-3.5 pointer-events-none text-black" />
      </div>

      {/* Currency Toggle */}
      <div className="hidden md:flex items-center rounded-none border border-black bg-white p-0.5 text-xs">
        <button
          onClick={() => setCurrency("INR")}
          className={`px-2 py-0.5 rounded-none transition-all font-mono font-bold text-[10px] ${
            currency === "INR"
              ? "bg-black text-white"
              : "text-black hover:bg-neutral-100"
          }`}
        >
          ₹ INR
        </button>
        <button
          onClick={() => setCurrency("USD")}
          className={`px-2 py-0.5 rounded-none transition-all font-mono font-bold text-[10px] ${
            currency === "USD"
              ? "bg-black text-white"
              : "text-black hover:bg-neutral-100"
          }`}
        >
          $ USD
        </button>
      </div>

      {/* Unit Scale Selector */}
      <div className="hidden lg:flex items-center rounded-none border border-black bg-white p-0.5 text-xs">
        {(["Cr", "Mn", "Bn", "K"] as const).map((scale) => (
          <button
            key={scale}
            onClick={() => setUnit(scale)}
            className={`px-1.5 py-0.5 rounded-none transition-all font-mono font-bold text-[10px] ${
              unit === scale
                ? "bg-black text-white"
                : "text-black hover:bg-neutral-100"
            }`}
          >
            {scale}
          </button>
        ))}
      </div>
    </div>
  );
}
