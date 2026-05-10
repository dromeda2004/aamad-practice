export function PlaceholderCards() {
  return (
    <section className="placeholders" aria-label="Future scope placeholders">
      <article className="card card--muted">
        <h3 className="card__title">Hiring dashboard (FR-4)</h3>
        <p className="muted">
          Funnel visibility and SLA timers are out of scope for the mini-project
          UI; this card reserves layout space for a future dashboard module.
        </p>
      </article>
      <article className="card card--muted">
        <h3 className="card__title">ATS sync</h3>
        <p className="muted">
          Full ATS read/write is deferred. Integration will map approved
          shortlist payloads to your ATS export format.
        </p>
      </article>
    </section>
  );
}
