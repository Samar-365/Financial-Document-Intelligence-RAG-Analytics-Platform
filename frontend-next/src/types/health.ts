export interface HealthStatusResponse {
  status: "ok" | "degraded" | "error";
  version: string;
  environment: string;
  components: {
    database: string;
  };
}
