export interface HealthStatusResponse {
  status: "ok" | "degraded" | "error" | "healthy";
  version: string;
  environment: string;
  components: {
    database: string;
  };
}

export type HealthStatus = HealthStatusResponse;
