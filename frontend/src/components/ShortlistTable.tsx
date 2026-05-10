import type { RecommendationRow } from "../api/types";

interface Props {
  rows: RecommendationRow[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ShortlistTable({ rows, selectedId, onSelect }: Props) {
  if (rows.length === 0) {
    return (
      <p className="muted">
        No recommendations yet. When the recommender stage completes, ranked
        candidates appear here.
      </p>
    );
  }

  return (
    <div className="table-wrap" role="region" aria-label="Ranked shortlist">
      <table className="data-table">
        <thead>
          <tr>
            <th scope="col">Rank</th>
            <th scope="col">Candidate</th>
            <th scope="col">Fit</th>
            <th scope="col">Top skills</th>
            <th scope="col">Rationale</th>
            <th scope="col">Signal</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const selected = selectedId === r.candidate_id;
            return (
              <tr
                key={r.candidate_id}
                className={selected ? "data-table__row data-table__row--selected" : "data-table__row"}
              >
                <td>{r.rank}</td>
                <td>
                  <button
                    type="button"
                    className="link-btn"
                    onClick={() => onSelect(r.candidate_id)}
                    aria-expanded={selected}
                  >
                    {r.display_name}
                  </button>
                </td>
                <td>{Math.round(r.fit_score * 100)}%</td>
                <td>{r.top_skills.slice(0, 3).join(", ")}</td>
                <td className="muted narrow">{r.rationale}</td>
                <td>
                  {r.uncertainty ? (
                    <span className="badge badge--warn">Low confidence</span>
                  ) : (
                    <span className="badge badge--ok">Stable</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
