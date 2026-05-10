import type { RecommendationRow } from "../api/types";

function toCsv(rows: RecommendationRow[]): string {
  const header = ["rank", "candidate_id", "display_name", "fit_score", "rationale"];
  const lines = [header.join(",")];
  for (const r of rows) {
    const esc = (s: string) => `"${s.replace(/"/g, '""')}"`;
    lines.push(
      [
        r.rank,
        r.candidate_id,
        esc(r.display_name),
        r.fit_score,
        esc(r.rationale),
      ].join(","),
    );
  }
  return lines.join("\n");
}

function download(filename: string, mime: string, body: string) {
  const blob = new Blob([body], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

interface Props {
  rows: RecommendationRow[];
  runId: string;
}

export function ExportToolbar({ rows, runId }: Props) {
  const hasData = rows.length > 0;

  return (
    <div className="export-toolbar" aria-label="Export shortlist">
      <button
        type="button"
        className="btn btn--ghost"
        disabled={!hasData}
        onClick={() =>
          download(
            `talentflow-shortlist-${runId}.json`,
            "application/json",
            JSON.stringify({ run_id: runId, recommendations: rows }, null, 2),
          )
        }
      >
        Export JSON
      </button>
      <button
        type="button"
        className="btn btn--ghost"
        disabled={!hasData}
        onClick={() =>
          download(
            `talentflow-shortlist-${runId}.csv`,
            "text/csv",
            toCsv(rows),
          )
        }
      >
        Export CSV
      </button>
    </div>
  );
}
