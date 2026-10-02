import { apiClient } from "@/lib/api-client";
import {
  DocumentItem,
  DocumentListResponse,
  DocumentUploadResponse,
} from "@/types/document";

export interface UploadDocumentParams {
  file: File;
  company_name?: string;
  fiscal_year?: number;
  fiscal_period?: string;
}

export const documentService = {
  async listDocuments(
    page: number = 1,
    pageSize: number = 50,
    status?: string
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (status) params.append("status", status);

    const { data } = await apiClient.get<DocumentListResponse>(
      `/documents?${params.toString()}`
    );
    return data;
  },

  async getDocument(documentId: string): Promise<DocumentItem> {
    const { data } = await apiClient.get<DocumentItem>(
      `/documents/${documentId}`
    );
    return data;
  },

  async uploadDocument(
    params: UploadDocumentParams
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append("file", params.file);
    if (params.company_name) formData.append("company_name", params.company_name);
    if (params.fiscal_year)
      formData.append("fiscal_year", params.fiscal_year.toString());
    if (params.fiscal_period)
      formData.append("fiscal_period", params.fiscal_period);

    const { data } = await apiClient.post<DocumentUploadResponse>(
      "/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return data;
  },

  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`);
  },
};
