export type EmploymentType = "full_time" | "part_time" | "contract" | "intern";

export type RunStage =
  | "pending"
  | "researching"
  | "evaluating"
  | "recommending"
  | "awaiting_approval"
  | "approved"
  | "failed"
  | "needs_clarification";

export interface RequisitionInput {
  role_title: string;
  must_have_skills: string[];
  preferred_skills: string[];
  experience_min_years: number;
  experience_max_years: number;
  location: string;
  employment_type: EmploymentType | "";
  free_text_brief: string;
}

export interface CandidatePoolItem {
  candidate_id: string;
  display_name: string;
  summary: string;
  source?: string;
  evidence?: string[];
  skills_matched?: string[];
}

export interface EvaluationRow {
  candidate_id: string;
  score_normalized: number;
  rationale: string;
  confidence: "high" | "medium" | "low";
  criteria_breakdown?: Record<string, number>;
}

export interface RecommendationRow {
  rank: number;
  candidate_id: string;
  display_name: string;
  fit_score: number;
  rationale: string;
  uncertainty: boolean;
  top_skills: string[];
}

export interface WorkflowRunPayload {
  run_id: string;
  trace_id?: string;
  stage: RunStage;
  error?: ApiErrorEnvelope;
  created_at?: string;
  candidate_pool?: CandidatePoolItem[];
  evaluations?: EvaluationRow[];
  recommendations?: RecommendationRow[];
}

export interface ApiErrorEnvelope {
  error_code: string;
  message: string;
  retryable?: boolean;
  suggested_action?: string;
  trace_id?: string;
}

export interface ApiClientOptions {
  baseUrl: string;
  getAuthHeaders?: () => Record<string, string>;
}
