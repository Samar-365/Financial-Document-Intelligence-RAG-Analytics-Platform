export interface QueryRequest {
  document_id: string;
  question: string;
  top_k?: number;
}

export interface Citation {
  document_id: string;
  page_number: number;
  snippet: string;
  relevance_score: number;
}

export interface RAGResponse {
  answer: string;
  citations: Citation[];
  latency_ms: number;
  model_used: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: Citation[];
  latency_ms?: number;
  model_used?: string;
  timestamp: string;
}
