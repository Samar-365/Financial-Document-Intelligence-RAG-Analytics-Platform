import { create } from "zustand";
import { persist } from "zustand/middleware";
import { DocumentItem } from "@/types/document";

interface WorkspaceState {
  activeDocumentId: string | null;
  activeDocument: DocumentItem | null;
  selectedCompany: string | null;
  selectedFiscalYear: number | null;
  currency: "INR" | "USD";
  unit: "Cr" | "Mn" | "Bn" | "K";
  
  // Actions
  setActiveDocument: (doc: DocumentItem | null) => void;
  setActiveDocumentId: (id: string | null) => void;
  setSelectedCompany: (company: string | null) => void;
  setSelectedFiscalYear: (year: number | null) => void;
  setCurrency: (currency: "INR" | "USD") => void;
  setUnit: (unit: "Cr" | "Mn" | "Bn" | "K") => void;
  resetWorkspace: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      activeDocumentId: null,
      activeDocument: null,
      selectedCompany: null,
      selectedFiscalYear: null,
      currency: "INR",
      unit: "Cr",

      setActiveDocument: (doc) =>
        set({
          activeDocument: doc,
          activeDocumentId: doc ? doc.id : null,
          selectedCompany: doc?.company_name || null,
          selectedFiscalYear: doc?.fiscal_year || null,
        }),

      setActiveDocumentId: (id) =>
        set({
          activeDocumentId: id,
        }),

      setSelectedCompany: (company) =>
        set({
          selectedCompany: company,
        }),

      setSelectedFiscalYear: (year) =>
        set({
          selectedFiscalYear: year,
        }),

      setCurrency: (currency) => set({ currency }),
      setUnit: (unit) => set({ unit }),
      
      resetWorkspace: () =>
        set({
          activeDocumentId: null,
          activeDocument: null,
          selectedCompany: null,
          selectedFiscalYear: null,
        }),
    }),
    {
      name: "findoc-workspace-storage",
    }
  )
);
