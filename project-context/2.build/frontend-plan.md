# Frontend Implementation Plan — TalentFlow AI

## Document Control
- Product: Recruitment Assistant Application (TalentFlow AI)
- Version: 1.0
- Date: 2026-05-10
- Owner Persona: `@frontend.eng`
- Inputs: `project-context/1.define/prd.md`, `project-context/2.build/sad.md`

---

## Status Tracking

| Area | Status | Notes |
|------|--------|--------|
| Plan document | Completed | This file |
| Vite + React + TS scaffold | Completed | `frontend/` |
| Role intake UI + validation | Completed | `RoleIntakeForm.tsx` |
| Run monitor + polling | Completed | `App.tsx` + SAD 2–5s / demo 2.6s cadence |
| Shortlist + detail panel | Completed | `ShortlistTable`, `CandidateDetailPanel` |
| API client + demo fallback | Completed | `src/api/client.ts`, `mock/demoRun.ts` |
| Export JSON/CSV | Completed | `ExportToolbar.tsx` |
| Placeholders (dashboard, ATS) | Completed | `PlaceholderCards.tsx` |
| Build verification | Completed | `npm run build` |

---

## UI Components To Build

1. **`App`** — Shell, header, demo toggle, live region toasts, orchestrates intake/monitor/shortlist.
2. **`RoleIntakeForm`** — Guided fields per PRD: title, must-have/preferred skills (comma-separated), experience min/max, location, employment type, optional brief; validation on title + ≥1 must-have skill; junior title + high years warning.
3. **`StageTimeline`** — Pipeline: Researcher → Evaluator → Recommender → Your review; failed / clarification / approved banners.
4. **Run monitor (in `App`)** — Run ID, trace when present, health/demomode banner, polling indicator via periodic refresh, error dismiss.
5. **`ShortlistTable`** — Ranked rows: rank, name, fit %, top skills, rationale, confidence badge.
6. **`CandidateDetailPanel`** — Criteria breakdown from evaluation map; “Compare top 3–5” stub per PRD comparison mode placeholder.
7. **`ReviewActions`** — Approve shortlist, rerun from researcher/evaluator (`POST` when API available).
8. **`ExportToolbar`** — JSON + CSV download for current recommendations.
9. **`PlaceholderCards`** — Non-functional FR-4 dashboard + ATS sync stubs (PRD out-of-scope).

---

## User Interaction Flows

1. **Intake → Start run**  
   Submit form → `POST /api/v1/runs` with `{ requisition }` when API healthy and demo off; on failure or demo on → local demo simulation with staged progression.

2. **Monitor**  
   - **API mode:** `GET /api/v1/runs/{run_id}` every ~3s until terminal or manual navigation away.  
   - **Demo mode:** automatic stage progression until `awaiting_approval`.

3. **Review recommendations**  
   Row select → detail panel; low-confidence rows flagged in table.

4. **Approve / Rerun**  
   - `POST /api/v1/runs/{run_id}/approve`  
   - `POST /api/v1/runs/{run_id}/rerun` with `{ from_stage: "researcher" | "evaluator" }` (evaluator maps to backend “evaluator”; recommender rerun can be added when contract finalizes).

5. **Export**  
   Client-side download of recommendations as JSON or CSV.

6. **Demo mode**  
   Toggle **Demo mode**; preference `localStorage` key `talentflow:useDemo`. Simulated data in `mock/demoRun.ts`.

---

## API Integration Points

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness probe at app load. |
| POST | `/api/v1/runs` | Body: `{ requisition: RequisitionInput }` → `{ run_id, stage, ... }`. |
| GET | `/api/v1/runs/{run_id}` | Poll status + stage payloads. |
| POST | `/api/v1/runs/{run_id}/rerun` | Body: `{ from_stage, notes? }`. |
| POST | `/api/v1/runs/{run_id}/approve` | Finalize recruiter-approved shortlist. |

- **Base URL:** `VITE_API_BASE_URL` in `frontend/.env.example`; empty string uses same-origin + **Vite proxy** to `http://localhost:8000` for `/api`.

---

## Implementation Approach

- **Stack:** Vite 5, React 18, TypeScript; global CSS with design tokens (WCAG-friendly contrast on dark theme).
- **State:** React hooks; no global store for MVP.
- **API layer:** Thin `fetch` wrapper + shared types; demo payload builder for offline UX.
- **Separation:** Presentation components under `src/components/`; integration can extend `client.ts` without refactoring UI.

---

## Implementation Log

- **2026-05-10:** Added `frontend-plan.md` scaffold and status table.
- **2026-05-10:** Scaffolded Vite + React + TS; implemented intake, timeline, shortlist, detail panel, export, review actions, placeholders, API client, demo simulator, proxy config.
- **2026-05-10:** `npm run build` passed (TypeScript + Vite production build).

---

## How To Run Locally

```powershell
Set-Location d:\aamad\test\frontend
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`). With no backend, use **Demo mode: on** or start a run — failed API calls also fall back to demo.

---

## Sources
- `project-context/1.define/prd.md`
- `project-context/2.build/sad.md`
- `.cursor/agents/frontend-eng.md`

## Assumptions
- FastAPI request/response shapes will align with the types in `frontend/src/api/types.ts`; minor field renames can be mapped in `client.ts`.
- `rerun` payload may be extended by integration; UI sends minimal `from_stage` today.

## Open Questions
- Exact backend JSON for `requisition` wrapper vs flat body — confirm with `@integration.eng`.
- Whether `from_stage` enums should be `researcher_agent` style vs short names.

## Audit
- Timestamp: 2026-05-10
- Persona: `@frontend.eng`
- Action: Delivered MVP frontend per PRD/SAD and updated this plan with final status.
