interface Props {
  disabled?: boolean;
  busy?: boolean;
  onApprove: () => void;
  onRerunResearcher: () => void;
  onRerunEvaluator: () => void;
}

export function ReviewActions({
  disabled,
  busy,
  onApprove,
  onRerunResearcher,
  onRerunEvaluator,
}: Props) {
  return (
    <div className="review-actions" role="group" aria-label="Recruiter review">
      <button
        type="button"
        className="btn btn--primary"
        disabled={disabled || busy}
        onClick={onApprove}
      >
        Approve shortlist
      </button>
      <button
        type="button"
        className="btn btn--ghost"
        disabled={disabled || busy}
        onClick={onRerunResearcher}
      >
        Rerun from researcher
      </button>
      <button
        type="button"
        className="btn btn--ghost"
        disabled={disabled || busy}
        onClick={onRerunEvaluator}
      >
        Rerun from evaluator
      </button>
    </div>
  );
}
