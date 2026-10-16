export interface CompareRequest {
  document_ids: string[];
  metric_names?: string[];
}

export interface DeltaItem {
  metric_name: string;
  values: Record<string, number>;
  absolute_delta: number;
  percent_delta: number;
}

export interface ComparisonResponse {
  document_ids: string[];
  deltas: DeltaItem[];
}
