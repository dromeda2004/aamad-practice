import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createApiClient } from "./api/client";
import type {
  EvaluationRow,
  RequisitionInput,
  RunStage,
  WorkflowRunPayload,
} from "./api/types";
import { CandidateDetailPanel } from "./components/CandidateDetailPanel";
import { ExportToolbar } from "./components/ExportToolbar";
import { PlaceholderCards } from "./components/PlaceholderCards";
import { ReviewActions } from "./components/ReviewActions";
import { RoleIntakeForm } from "./components/RoleIntakeForm";
import { ShortlistTable } from "./components/ShortlistTable";
import { StageTimeline } from "./components/StageTimeline";
import {
  buildDemoPayload,
  newDemoRunId,
  nextDemoStage,
} from "./mock/demoRun";

const STORAGE_DEMO = "talentflow:useDemo";

export function App() {
  const baseUrl = useMemo(
    () => (import.meta.env.VITE_API_BASE_URL ?? "").trim(),
    [],
  );
  const client = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);

  const [useDemo, setUseDemo] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_DEMO) === "true";
    } catch {
      return false;
    }
  });
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [requisition, setRequisition] = useState<RequisitionInput | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [run, setRun] = useState<WorkflowRunPayload | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [pollError, setPollError] = useState<string | null>(null);

  const demoStageRef = useRef<RunStage>("pending");

  /** Probe backend health once at load (informational). */
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const ok = await client.healthCheck();
      if (!cancelled) setBackendOk(ok);
    })();
    return () => {
      cancelled = true;
    };
  }, [client]);

  const announce = useCallback((msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 4000);
  }, []);

  const startDemoProgression = useCallback(
    (id: string, req: RequisitionInput) => {
      demoStageRef.current = "researching";
      setRun(buildDemoPayload(req, id, "researching"));
      announce("Demo mode: simulating researcher stage.");
    },
    [announce],
  );

  useEffect(() => {
    if (!useDemo || !runId || !requisition) return;
    if (
      run?.stage === "awaiting_approval" ||
      run?.stage === "approved" ||
      run?.stage === "failed"
    ) {
      return;
    }

    const timer = window.setInterval(() => {
      const cur = demoStageRef.current;
      const nxt =
        cur === "awaiting_approval" ? "awaiting_approval" : nextDemoStage(cur);
      demoStageRef.current = nxt;
      const payload = buildDemoPayload(requisition, runId, nxt);
      setRun(payload);
      if (nxt === "awaiting_approval") {
        announce("Demo: shortlist ready for your review.");
        window.clearInterval(timer);
      }
    }, 2600);

    return () => window.clearInterval(timer);
  }, [useDemo, runId, requisition, run?.stage, announce]);

  useEffect(() => {
    if (useDemo || !runId) return;
    const activeRunId = runId;

    let cancelled = false;
    async function poll() {
      try {
        const next = await client.getRun(activeRunId);
        if (cancelled) return;
        setRun(next);
        setPollError(null);
      } catch (e) {
        if (!cancelled) {
          setPollError(
            e instanceof Error ? e.message : "Failed to refresh run status.",
          );
        }
      }
    }

    poll();
    const id = window.setInterval(poll, 3000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [useDemo, runId, client]);

  const handleIntakeSubmit = async (payload: RequisitionInput) => {
    setBusy(true);
    setRequisition(payload);
    setPollError(null);
    setSelectedId(null);
    demoStageRef.current = "pending";

    try {
      if (useDemo || backendOk === false) {
        const id = newDemoRunId();
        setRunId(id);
        demoStageRef.current = "pending";
        startDemoProgression(id, payload);
      } else {
        const created = await client.createRun(payload);
        setRunId(created.run_id);
        setRun(created);
        announce(`Run started: ${created.run_id}`);
      }
    } catch (e) {
      const id = newDemoRunId();
      setRunId(id);
      setUseDemo(true);
      try {
        localStorage.setItem(STORAGE_DEMO, "true");
      } catch {
        /* ignore */
      }
      announce("API unavailable — switched to demo simulation.");
      startDemoProgression(id, payload);
    } finally {
      setBusy(false);
    }
  };

  const toggleDemo = () => {
    const next = !useDemo;
    setUseDemo(next);
    try {
      localStorage.setItem(STORAGE_DEMO, next ? "true" : "false");
    } catch {
      /* ignore */
    }
    setRun(null);
    setRunId(null);
    setPollError(null);
    announce(next ? "Demo mode enabled." : "Demo mode disabled — will use API when available.");
  };

  const handleApprove = async () => {
    if (!runId) return;
    setBusy(true);
    try {
      if (useDemo && requisition) {
        setRun(buildDemoPayload(requisition, runId, "approved"));
        announce("Shortlist marked approved (demo).");
      } else {
        const next = await client.approveRun(runId);
        setRun(next);
        announce("Shortlist approved.");
      }
    } catch (e) {
      setPollError(
        e instanceof Error ? e.message : "Approve failed. Try demo mode.",
      );
    } finally {
      setBusy(false);
    }
  };

  const handleRerun = async (from: "researcher" | "evaluator") => {
    if (!runId) return;
    setBusy(true);
    try {
      if (useDemo && requisition) {
        const stage: RunStage =
          from === "researcher" ? "researching" : "evaluating";
        demoStageRef.current = stage;
        setRun(buildDemoPayload(requisition, runId, stage));
        announce(`Demo rerun from ${from}.`);
      } else {
        const next = await client.rerunFromStage(runId, { from_stage: from });
        setRun(next);
      }
    } catch (e) {
      setPollError(
        e instanceof Error ? e.message : "Rerun failed. Try demo mode.",
      );
    } finally {
      setBusy(false);
    }
  };

  const evalById = useMemo(() => {
    const map = new Map<string, EvaluationRow>();
    if (run?.evaluations) {
      for (const ev of run.evaluations) {
        map.set(ev.candidate_id, ev);
      }
    }
    return map;
  }, [run?.evaluations]);

  const selectedName =
    run?.recommendations?.find((r) => r.candidate_id === selectedId)
      ?.display_name ?? "";

  const stage = run?.stage ?? "pending";
  const showShortlist =
    stage === "awaiting_approval" ||
    stage === "approved" ||
    (run?.recommendations?.length ?? 0) > 0;

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <h1>TalentFlow AI</h1>
          <p className="tagline">Speed with trust — recruitment assistant MVP</p>
        </div>
        <div className="header-actions">
          <span className="pill" title="SAD default runtime">
            Runtime: crewai
          </span>
          <button type="button" className="btn btn--ghost" onClick={toggleDemo}>
            {useDemo ? "Demo mode: on" : "Demo mode: off"}
          </button>
        </div>
      </header>

      <main className="app__main">
        <section className="grid-main">
          <RoleIntakeForm onSubmit={handleIntakeSubmit} disabled={busy} />

          <div className="panel">
            <h2 className="panel__title">Run monitor</h2>
            <p className="muted">
              API base:{" "}
              <code>{baseUrl || "(same origin + Vite proxy → :8000)"}</code>
              {backendOk === null && " — checking health…"}
              {backendOk === true && !useDemo && " — backend reachable."}
              {(useDemo || backendOk === false) && " — using demo simulation."}
            </p>

            {runId && (
              <p>
                <strong>Run ID:</strong>{" "}
                <code>{runId}</code>
                {run?.trace_id && (
                  <>
                    {" "}
                    <span className="muted">· trace</span>{" "}
                    <code>{run.trace_id}</code>
                  </>
                )}
              </p>
            )}

            <StageTimeline stage={stage} />

            {pollError && (
              <div className="banner banner--error" role="alert">
                {pollError}{" "}
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => setPollError(null)}
                >
                  Dismiss
                </button>
              </div>
            )}

            {run?.error && (
              <div className="banner banner--error" role="alert">
                <strong>{run.error.error_code}</strong>: {run.error.message}
                {run.error.suggested_action && (
                  <p className="tiny">{run.error.suggested_action}</p>
                )}
              </div>
            )}

            {showShortlist && run?.recommendations && (
              <>
                <div className="split">
                  <div>
                    <div className="toolbar">
                      <h3 className="subhead">Ranked recommendations</h3>
                      <ExportToolbar rows={run.recommendations} runId={runId!} />
                    </div>
                    <ShortlistTable
                      rows={run.recommendations}
                      selectedId={selectedId}
                      onSelect={setSelectedId}
                    />
                    {stage === "awaiting_approval" && (
                      <ReviewActions
                        busy={busy}
                        onApprove={handleApprove}
                        onRerunResearcher={() => handleRerun("researcher")}
                        onRerunEvaluator={() => handleRerun("evaluator")}
                      />
                    )}
                  </div>
                  <CandidateDetailPanel
                    candidateName={selectedName}
                    evaluation={
                      selectedId ? evalById.get(selectedId) : undefined
                    }
                    onCompareTop={() =>
                      announce("Comparison mode stub — reserve for top 3–5 view.")
                    }
                  />
                </div>
              </>
            )}
          </div>

          <PlaceholderCards />
        </section>
      </main>

      <footer className="app__footer">
        <small>
          Human-in-the-loop by design — approvals gate hiring manager handoff.
        </small>
      </footer>

      <div className="live-region" role="status" aria-live="polite" aria-atomic="true">
        {toast ?? ""}
      </div>
    </div>
  );
}
