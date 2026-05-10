import type { EvaluationRow } from "../api/types";

interface Props {
  candidateName: string;
  evaluation?: EvaluationRow;
  onCompareTop?: () => void;
}

export function CandidateDetailPanel({
  candidateName,
  evaluation,
  onCompareTop,
}: Props) {
  if (!evaluation) {
    return (
      <aside className="panel panel--aside" aria-label="Candidate detail">
        <h3 className="panel__title">Candidate detail</h3>
        <p className="muted">Select a row to see criteria breakdown.</p>
      </aside>
    );
  }

  const entries = Object.entries(evaluation.criteria_breakdown ?? {});

  return (
    <aside className="panel panel--aside" aria-label="Candidate detail">
      <h3 className="panel__title">{candidateName}</h3>
      <p className="muted">
        Confidence:{" "}
        <strong>{evaluation.confidence}</strong>
      </p>
      <p>{evaluation.rationale}</p>

      {entries.length > 0 && (
        <>
          <h4 className="subhead">Criteria (demo scale 1–5)</h4>
          <ul className="criteria-list">
            {entries.map(([k, v]) => (
              <li key={k}>
                <span>{k.replaceAll("_", " ")}</span>
                <span className="criteria-list__score">{v}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      <div className="actions-row">
        <button type="button" className="btn btn--ghost" onClick={onCompareTop}>
          Compare top 3–5 (stub)
        </button>
      </div>
      <p className="tiny muted">
        Full evidence traceability ties to job criteria and candidate evidence
        when backend returns source snippets.
      </p>
    </aside>
  );
}
