export interface FinancialMetricItem {
  metric_name: string;
  value?: number | null;
  unit: string;
  fiscal_year?: number | null;
  fiscal_period?: string | null;
  source_page?: number | null;
  confidence: number;
}

export interface FinancialMetricsResponse {
  document_id: string;
  metrics: FinancialMetricItem[];
}

export interface FinancialRatiosResponse {
  document_id: string;
  opm?: number | null;
  npm?: number | null;
  roe?: number | null;
  roce?: number | null;
  current_ratio?: number | null;
  quick_ratio?: number | null;
  debt_to_equity?: number | null;
  interest_coverage?: number | null;
}

export interface HealthScoreResponse {
  document_id: string;
  overall_score: number;
  growth_score: number;
  profitability_score: number;
  liquidity_score: number;
  leverage_score: number;
  cash_flow_score: number;
  risk_flags: string[];
}
