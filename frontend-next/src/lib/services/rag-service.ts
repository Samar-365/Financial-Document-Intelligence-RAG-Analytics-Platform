import { apiClient } from "@/lib/api-client";
import { QueryRequest, RAGResponse } from "@/types/rag";

export const ragService = {
  async query(payload: QueryRequest): Promise<RAGResponse> {
    const { data } = await apiClient.post<RAGResponse>("/query", {
      document_id: payload.document_id,
      question: payload.question,
      top_k: payload.top_k ?? 5,
    });
    return data;
  },
};
