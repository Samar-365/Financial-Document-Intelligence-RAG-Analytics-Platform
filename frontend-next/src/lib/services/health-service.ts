import { apiClient } from "@/lib/api-client";
import { HealthStatusResponse } from "@/types/health";

export const healthService = {
  async getHealth(): Promise<HealthStatusResponse> {
    const { data } = await apiClient.get<HealthStatusResponse>("/health");
    return data;
  },
};
