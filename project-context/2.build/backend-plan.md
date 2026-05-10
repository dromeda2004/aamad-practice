# Backend Implementation Plan — TalentFlow AI (CrewAI + FastAPI)

## Document Control
- Version: 1.0
- Date: 2026-05-10
- Runtime: `crewai` (`AAMAD_TARGET_RUNTIME=crewai`)
- Inputs: `project-context/1.define/prd.md`, `project-context/2.build/sad.md`, frontend API contract (`frontend/src/api/client.ts`)

---

## Status Tracking

| Area | Status | Notes |
|------|--------|--------|
| backend-plan.md | Completed | Updated with final status & log |
| `project-context/2.build/backend.md` | Completed | Persona-required artifact |
| `backend/config/agents.yaml`, `backend/config/tasks.yaml` | Completed | Externalized per CrewAI adapter |
| `backend/crew.py` (CrewAI builders) | Completed | Three sequential mini-crews |
| `backend/app/` (FastAPI + pipeline + store + mock) | Completed | In-memory store (no DB per MVP boundary) |
| API routes | Completed | Matches frontend client |
| Mock / auto-mock mode | Completed | `USE_MOCK_CREW` + `OPENAI_API_KEY` auto |
| Local verification | Completed | `fastapi.testclient` flow (create → poll → approve) with `USE_MOCK_CREW=true` |
| `pip install -r backend/requirements.txt` | Completed | Installed in dev environment (exit 0) |

---

## Application Crew (CrewAI)

### Agents (YAML)
- **researcher**: evidence-first candidate pool synthesis from requisition JSON.
- **evaluator**: rubric scoring with confidence and optional criteria breakdown.
- **recommender**: ranked output with uncertainty flags.

### Orchestration
- **Three mini-crews** (process `sequential`), each with `allow_delegation=false` and `memory=false`.
- Prompts require **raw JSON only**; server parses with `json.loads` + fenced-code stripping.

### Controls
- Env: `CREW_MAX_RPM`, `CREW_MAX_ITER` (capped at 12), optional `OPENAI_MODEL` / `CREW_MODEL`.

---

## API Endpoints (FastAPI)

Per SAD §4; JSON matches `WorkflowRunPayload` in the frontend.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | `{ "status": "ok" }` |
| POST | `/api/v1/runs` | Create run from `{ "requisition": RequisitionInput }` |
| GET | `/api/v1/runs/{run_id}` | Poll status + artifacts |
| POST | `/api/v1/runs/{run_id}/rerun` | `from_stage`: researcher / evaluator / recommender |
| POST | `/api/v1/runs/{run_id}/approve` | Approve gate from `awaiting_approval` → `approved` |

---

## Business Logic Components

- **Stage machine:** `researching → evaluating → recommending → awaiting_approval → approved | failed`.
- **Rerun rules:**
  - `researcher` — clears pool + downstream artifacts.
  - `evaluator` — clears evaluations + recommendations (keeps pool).
  - `recommender` — clears recommendations (keeps pool + evaluations).
- **JSON validation:** pydantic validates pool/evals/rec rows after Crew or mock emission.
- **Errors:** persisted on the run (`failed`) with `ApiErrorEnvelope` fields.

---

## Implementation Approach

- **Location:** `backend/` with `pip install -r requirements.txt`; run `uvicorn app.main:app` from `backend/`.
- **`crew.py`** is the YAML-backed Crew wiring entry referenced by adapter guidance.
- **Mock fallback:** deterministic pipeline for demos/CI/offline (`USE_MOCK_CREW=true` or `USE_MOCK_CREW=auto` with no API key).
- **Deferrals (@backend.eng persona):** no external integrations/analytics/database.

---

## Implementation Log

- **2026-05-10:** Scaffolded plan; added YAML agents/tasks; wired `crew.py` + synchronous pipeline + FastAPI endpoints; in-memory `RunStore`.
- **2026-05-10:** Fixed pipeline error helper signature bug and removed thread-pool wrapper for mock path (TestClient + executor edge cases).
- **2026-05-10:** Verified end-to-end `TestClient` flow with `USE_MOCK_CREW=true` (create → awaiting_approval → approve).
- **2026-05-10:** Added `backend/.env.example` and extended root `.env.example` with backend toggles.

---

## How To Run

```powershell
Set-Location d:\aamad\test\backend
pip install -r requirements.txt
$env:USE_MOCK_CREW="true"   # or configure OPENAI_API_KEY for real CrewAI kickoff
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (`frontend/`) can continue to rely on Vite proxy to `http://127.0.0.1:8000`.

---

## Sources
- `project-context/1.define/prd.md`
- `project-context/2.build/sad.md`
- `.cursor/rules/adapter-crewai.mdc`
- `.cursor/agents/backend-eng.md`

---

## Assumptions
- Frontend remains the contractual source for response field names (`WorkflowRunPayload`).

## Open Questions
- Production hardening should offload synchronous `crew.kickoff()` via `asyncio.to_thread` and add request timeouts/idempotency keys per SAD.
- Optional Bearer/API-key enforcement deferred (`API_KEY` placeholder in `.env.example`).

---

## Audit
- Timestamp: 2026-05-10
- Persona: `@backend.eng`
- Action: Implemented MVP backend plan + codebase; refreshed this document with completion status.
