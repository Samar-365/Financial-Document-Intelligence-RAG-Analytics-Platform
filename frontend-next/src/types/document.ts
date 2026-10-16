export type DocumentStatus =
  | "UPLOADED"
  | "PROCESSING"
  | "PARSED"
  | "INDEXED"
  | "COMPLETED"
  | "FAILED";

export interface DocumentItem {
  id: string;
  filename: string;
  file_hash: string;
  file_size_bytes?: number | null;
  page_count?: number | null;
  status: DocumentStatus | string;
  company_name?: string | null;
  fiscal_year?: number | null;
  fiscal_period?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
