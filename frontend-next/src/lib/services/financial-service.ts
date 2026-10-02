import { apiClient } from "@/lib/api-client";
import { ComparisonResponse } from "@/types/comparison";
import {
  FinancialMetricsResponse,
  FinancialRatiosResponse,
  HealthScoreResponse,
} from "@/types/financial";

export const financialService = {
  async getMetrics(documentId: string): Promise<FinancialMetricsResponse> {
    const { data } = await apiClient.get<FinancialMetricsResponse>(
      `/financial-metrics/${documentId}`
    );
    return data;
  },

  async getRatios(documentId: string): Promise<FinancialRatiosResponse> {
    const { data } = await apiClient.get<FinancialRatiosResponse>(
      `/financial-ratios/${documentId}`
    );
    return data;
  },

  async getHealthScore(documentId: string): Promise<HealthScoreResponse> {
    const { data } = await apiClient.get<HealthScoreResponse>(
      `/health-score/${documentId}`
    );
    return data;
  },

  async compareDocuments(
    documentIds: string[],
    metricNames?: string[]
  ): Promise<ComparisonResponse> {
    const { data } = await apiClient.post<ComparisonResponse>("/compare", {
      document_ids: documentIds,
      metric_names: metricNames || [],
    });
    return data;
  },
};
