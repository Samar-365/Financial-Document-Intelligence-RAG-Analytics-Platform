"use client";

import React, { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { documentService } from "@/lib/services/document-service";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Building2, FileText, ChevronDown, Check, Coins } from "lucide-react";

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
        <div className="absolute left-3 pointer-events-none text-slate-400">
          <Building2 className="h-4 w-4" />
        </div>
        <select
          value={activeDocumentId || ""}
          onChange={handleDocumentChange}
          disabled={isLoading || documents.length === 0}
          className="h-9 pl-9 pr-8 bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/60 rounded-lg text-xs font-medium text-slate-100 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer min-w-[200px] max-w-[280px] truncate shadow-sm transition-all"
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
        <ChevronDown className="absolute right-2.5 h-3.5 w-3.5 pointer-events-none text-slate-400" />
      </div>

      {/* Currency Toggle */}
      <div className="hidden md:flex items-center rounded-lg border border-slate-700/60 bg-slate-900/80 p-0.5 text-xs">
        <button
          onClick={() => setCurrency("INR")}
          className={`px-2 py-1 rounded-md transition-all font-semibold ${
            currency === "INR"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          ₹ INR
        </button>
        <button
          onClick={() => setCurrency("USD")}
          className={`px-2 py-1 rounded-md transition-all font-semibold ${
            currency === "USD"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          $ USD
        </button>
      </div>

      {/* Unit Scale Selector */}
      <div className="hidden lg:flex items-center rounded-lg border border-slate-700/60 bg-slate-900/80 p-0.5 text-xs">
        {(["Cr", "Mn", "Bn", "K"] as const).map((scale) => (
          <button
            key={scale}
            onClick={() => setUnit(scale)}
            className={`px-2 py-1 rounded-md transition-all font-medium ${
              unit === scale
                ? "bg-slate-700 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {scale}
          </button>
        ))}
      </div>
    </div>
  );
}
