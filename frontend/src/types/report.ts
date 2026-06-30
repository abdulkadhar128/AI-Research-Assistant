export interface Report {
  id: number;
  query: string;
  report: string;
  quality_score: number;
  review_feedback: string;
  citations: string;
  created_at: string;
}

export interface ResearchResponse {
  report_id: number;
  report: string;
  quality_score: number;
}
