import type {
  CandidatePoolItem,
  EvaluationRow,
  RequisitionInput,
  RecommendationRow,
  RunStage,
  WorkflowRunPayload,
} from "../api/types";

let demoSeq = 0;

function demoShortlist(seed: string): RecommendationRow[] {
  const suffix = seed.slice(-4);
  return [
    {
      rank: 1,
      candidate_id: `c-${suffix}-001`,
      display_name: "Alex Rivera",
      fit_score: 0.92,
      rationale:
        "Strong overlap on must-have skills with recent ownership of comparable hiring pipelines.",
      uncertainty: false,
      top_skills: ["Sourcing strategy", "ATS hygiene", "Stakeholder comms"],
    },
    {
      rank: 2,
      candidate_id: `c-${suffix}-002`,
      display_name: "Jordan Kim",
      fit_score: 0.87,
      rationale:
        "Excellent technical depth with slightly lighter volume hiring experience.",
      uncertainty: true,
      top_skills: ["Technical recruiting", "Engineering pipelines"],
    },
    {
      rank: 3,
      candidate_id: `c-${suffix}-003`,
      display_name: "Sam Patel",
      fit_score: 0.82,
      rationale:
        "Broad recruiting fundamentals; may need onboarding on tooling stack.",
      uncertainty: false,
      top_skills: ["Interview design", "Diversity sourcing"],
    },
  ];
}

export function demoPool(requisition: RequisitionInput): CandidatePoolItem[] {
  const skillsSample = [...requisition.must_have_skills, ...requisition.preferred_skills].slice(0, 5);
  return demoShortlist(`pool-${requisition.role_title}`).map((r, i) => ({
    candidate_id: r.candidate_id,
    display_name: r.display_name,
    summary:
      `${r.display_name}: ${skillsSample.slice(0, 2).join(", ") || "recruiting"} experienced professional.`,
    source: i === 0 ? "connector:demo" : "import:manual",
    evidence: [
      `Matched skills: ${skillsSample.slice(0, 3).join(", ") || "role criteria"}`,
      requisition.free_text_brief
        ? "Brief excerpt used for clarification context."
        : "Structured intake used without free-text augmentation.",
    ],
    skills_matched: skillsSample,
  }));
}

export function demoEvaluations(rows: RecommendationRow[]): EvaluationRow[] {
  return rows.map((r) => ({
    candidate_id: r.candidate_id,
    score_normalized: r.fit_score,
    rationale: r.rationale,
    confidence: r.uncertainty ? "medium" : "high",
    criteria_breakdown: {
      Must_have_skills: Math.min(5, Math.round(r.fit_score * 5)),
      Impact: Math.min(5, Math.round(r.fit_score * 4)),
      Collaboration: Math.min(5, Math.round(r.fit_score * 4.5)),
    },
  }));
}

/** Deterministic-ish demo run id */
export function newDemoRunId(): string {
  demoSeq += 1;
  return `demo-${Date.now()}-${demoSeq}`;
}

/** Advance demo workflow by fixed stage transitions for offline UX. */
export function buildDemoPayload(
  requisition: RequisitionInput | null,
  runId: string,
  stage: RunStage,
  approvedHint = false,
): WorkflowRunPayload {
  const recommendations = demoShortlist(runId);

  switch (stage) {
    case "pending":
      return { run_id: runId, stage: "pending" };
    case "researching":
      return {
        run_id: runId,
        stage: "researching",
        trace_id: `trace-${runId}`,
        candidate_pool: requisition ? demoPool(requisition) : undefined,
      };
    case "evaluating":
      return {
        run_id: runId,
        stage: "evaluating",
        trace_id: `trace-${runId}`,
        candidate_pool: requisition ? demoPool(requisition) : undefined,
      };
    case "recommending":
      return {
        run_id: runId,
        stage: "recommending",
        trace_id: `trace-${runId}`,
        evaluations: demoEvaluations(recommendations),
        candidate_pool: requisition ? demoPool(requisition) : undefined,
      };
    case "awaiting_approval":
      return {
        run_id: runId,
        stage: "awaiting_approval",
        trace_id: `trace-${runId}`,
        candidate_pool: requisition ? demoPool(requisition) : undefined,
        evaluations: demoEvaluations(recommendations),
        recommendations,
      };
    case "approved":
      return {
        run_id: runId,
        stage: "approved",
        trace_id: `trace-${runId}`,
        candidate_pool: requisition ? demoPool(requisition) : undefined,
        evaluations: demoEvaluations(recommendations),
        recommendations,
      };
    case "failed":
      return {
        run_id: runId,
        stage: "failed",
        trace_id: `trace-${runId}`,
        error: {
          error_code: "demo_timeout",
          message: "Simulated upstream timeout. Preserve intermediate artifacts and retry.",
          retryable: true,
          suggested_action: "Retry from evaluator or broaden filters and rerun researcher.",
          trace_id: `trace-${runId}`,
        },
      };
    default:
      return {
        run_id: runId,
        stage,
        recommendations: approvedHint ? recommendations : undefined,
      };
  }
}

const sequence: RunStage[] = [
  "pending",
  "researching",
  "evaluating",
  "recommending",
  "awaiting_approval",
];

export function nextDemoStage(current: RunStage): RunStage {
  const idx = sequence.indexOf(current);
  if (idx === -1) return current;
  if (idx >= sequence.length - 1) return "awaiting_approval";
  return sequence[idx + 1]!;
}
