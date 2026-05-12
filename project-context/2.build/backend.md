# Backend Artifact — TalentFlow AI (MVP)

## Runtime
- **Resolved:** `AAMAD_TARGET_RUNTIME=crewai` (per PRD / SAD / project convention)

## What Was Implemented
- **FastAPI** service under `backend/app/main.py` with routes aligned to the frontend client:
  - `GET /api/v1/health`
  - `POST /api/v1/runs` — body `{ "requisition": { ... } }`
  - `GET /api/v1/runs/{run_id}`
  - `POST /api/v1/runs/{run_id}/rerun` — `{ "from_stage": "researcher"|"evaluator"|"recommender", "notes": optional }`
  - `POST /api/v1/runs/{run_id}/approve`
- **CrewAI wiring** (`backend/crew.py`) reads externalized personas from `backend/config/agents.yaml` and expectations from `backend/config/tasks.yaml`, then constructs **three sequential mini-crews** (one agent → one JSON-only task): researcher, evaluator, recommender.
- **Pipeline** (`backend/app/pipeline.py`) advances stages explicitly so polling can observe `researching → evaluating → recommending → awaiting_approval`.
- **In-memory run store** (`backend/app/store.py`) — no PostgreSQL per `@backend.eng` MVP boundary.
- **Deterministic fallback** (`USE_MOCK_CREW` / missing API key auto mode): `backend/app/mock_crew.py` returns schema-valid payloads for local dev/tests.

## How To Run Locally
From `backend/`:

```powershell
pip install -r requirements.txt
$env:USE_MOCK_CREW="true"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The Vite frontend dev server proxies `/api` to `localhost:8000` when `VITE_API_BASE_URL` is unset.

## Non-MVP (Deferred)
- PostgreSQL persistence, ATS/email/calendar connectors, funnel analytics dashboards, SSO/RBAC beyond optional `API_KEY` stub noted in env example.

## Known Notes
- **Blocking LLM execution:** CrewAI kickoff runs synchronously on the asyncio event loop in this MVP. For heavier models, offload with `asyncio.to_thread(...)` around `run_*` when `should_use_mock_crew()` is false.

## Sources
- `project-context/1.define/prd.md`
- `project-context/2.build/sad.md`
- `.cursor/agents/backend-eng.md`
- `.cursor/rules/adapter-crewai.mdc`

## Audit
- Timestamp: 2026-05-10
- Persona: `@backend.eng`
- Action: Implemented FastAPI MVP + CrewAI application crew scaffolding with YAML-externalized agents/tasks and documented runtime controls.
