export interface Report {
  id: number;
  query: string;
  report: string;
  quality_score: number;
  review_feedback: string;
  citations: string;
  generation_time: number | null;
  created_at: string;
}

export interface ResearchResponse {
  report_id: number;
  report: string;
  quality_score: number;
  generation_time: number;
}
