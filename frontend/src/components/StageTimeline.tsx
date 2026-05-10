import type { RunStage } from "../api/types";

const STAGES: { key: RunStage; label: string }[] = [
  { key: "researching", label: "Researcher" },
  { key: "evaluating", label: "Evaluator" },
  { key: "recommending", label: "Recommender" },
  { key: "awaiting_approval", label: "Your review" },
];

const order: Record<string, number> = {
  pending: 0,
  researching: 1,
  evaluating: 2,
  recommending: 3,
  awaiting_approval: 4,
  approved: 5,
};

interface Props {
  stage: RunStage;
}

export function StageTimeline({ stage }: Props) {
  const idx = order[stage] ?? 0;
  const failed = stage === "failed";
  const clarification = stage === "needs_clarification";

  return (
    <div className="timeline" aria-label="Workflow stage">
      <ol className="timeline__list">
        {STAGES.map(({ key, label }) => {
          const stepIndex = order[key] ?? 0;
          const done = idx > stepIndex && !failed && !clarification;
          const active = stage === key;

          return (
            <li
              key={key}
              className={`timeline__item ${done ? "timeline__item--done" : ""} ${active ? "timeline__item--active" : ""}`}
            >
              <span className="timeline__dot" aria-hidden />
              <span>{label}</span>
            </li>
          );
        })}
      </ol>

      {failed && (
        <p className="banner banner--error" role="alert">
          Run failed. Use retry actions or contact integration if the error
          persists.
        </p>
      )}
      {clarification && (
        <p className="banner banner--warn" role="status">
          Clarification needed from intake before sourcing can continue.
        </p>
      )}
      {stage === "approved" && (
        <p className="banner banner--ok" role="status">
          Shortlist approved and ready for hiring manager handoff.
        </p>
      )}
    </div>
  );
}
