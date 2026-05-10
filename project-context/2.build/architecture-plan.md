# Architecture Implementation Plan

## Document Control
- Product: Recruitment Assistant Application (TalentFlow AI)
- Version: 1.0
- Date: 2026-05-10
- Owner Persona: `@system.arch`
- Related SAD: `project-context/2.build/sad.md`

## Objective
Implement the MVP architecture defined in the SAD with deterministic CrewAI orchestration, a recruiter-focused web UI, and a FastAPI backend that provides reliable and auditable workflow execution.

## Scope
- In scope:
  - CrewAI application crew (`researcher_agent`, `evaluator_agent`, `recommender_agent`)
  - FastAPI API for run orchestration and state retrieval
  - Web UI for intake, status monitoring, recommendation review, and approval
  - Core persistence, observability, and security baseline
- Out of scope:
  - Full ATS bidirectional integration
  - Candidate communication automation
  - Predictive analytics features

## Implementation Approach

### Phase 1: Foundation and Contracts
- Define API schemas and state machine for workflow runs.
- Define handoff data contracts between the three agents.
- Scaffold project structure:
  - backend service (`FastAPI`)
  - crew worker service (`CrewAI`)
  - frontend web app (`React + TypeScript`)
- Establish baseline environment variables and secret handling.

### Phase 2: Multi-Agent Core
- Configure `config/agents.yaml` and `config/tasks.yaml`.
- Implement sequential task flow with stage-level retry/timeouts.
- Implement stage output persistence and audit events.
- Add quality checks:
  - candidate pool threshold gate
  - evaluator confidence gate.

### Phase 3: API and Integration Layer
- Implement API endpoints for run lifecycle:
  - create, status, rerun, approve, health.
- Add request validation and error envelope standardization.
- Integrate backend orchestration calls to crew worker.
- Add initial connector abstraction and fallback manual import path.

### Phase 4: Frontend Experience
- Build role intake form with required validation.
- Build run monitor page with live stage progression.
- Build recommendation review table and detail panel.
- Add recruiter actions:
  - approve
  - rerun with revised criteria
  - rerun from specific stage.

### Phase 5: Quality, Security, and Release
- Add unit, integration, and E2E tests for critical flows.
- Implement RBAC baseline and secure secret management.
- Configure structured logging, trace IDs, and operational dashboards.
- Run staging validation and pilot readiness checklist.

## Work Breakdown and Status

| Workstream | Owner | Key Deliverables | Status |
|---|---|---|---|
| Architecture contracts | System Architect + Backend | API schemas, handoff schemas, state model | Completed (documented) |
| Crew setup | Backend Engineer | agents/tasks YAML, crew entrypoint, retry controls | Planned |
| Backend API | Backend Engineer | FastAPI endpoints + validation + error handling | Planned |
| Frontend UI | Frontend Engineer | Intake, monitor, recommendations, approval UX | Planned |
| Data layer | Backend Engineer | run/state/audit persistence schema | Planned |
| Integration adapters | Integration Engineer | source connector abstraction + fallback paths | Planned |
| QA automation | QA Engineer | unit/integration/E2E tests + smoke tests | Planned |
| Observability | Backend + Integration | logs, trace IDs, alerts, basic dashboards | Planned |

## Milestones
- M1 (Week 1-2): Contracts and service scaffolds complete.
- M2 (Week 3-4): End-to-end crew run via API with persisted stage outputs.
- M3 (Week 5-6): Recruiter web flow complete (intake -> monitor -> recommendations -> approve).
- M4 (Week 7-8): Test hardening, observability baseline, staging pilot readiness.

## Risks and Mitigations
- Integration variability risk:
  - Mitigation: connector abstraction + manual import fallback in MVP.
- Recommendation trust risk:
  - Mitigation: rationale-first UI, confidence indicators, mandatory approval gate.
- Runtime instability risk:
  - Mitigation: stage retries, timeouts, idempotent run IDs, clear failure envelopes.
- Scope expansion risk:
  - Mitigation: strict MVP boundary and deferred feature list tied to KPI thresholds.

## Definition of Done
- Recruiter can complete one full workflow from intake to approved shortlist.
- All three agents execute sequentially with persisted artifacts and audit logs.
- API contracts validated by integration tests.
- UI handles low-confidence/no-candidate/failure paths with user recovery actions.
- Pilot readiness checklist completed in staging.

## Status Summary
- Current status: **Planning Complete**
- SAD readiness: **Complete**
- Implementation readiness: **Ready to start Phase 1**
- Next step: backend and crew contract scaffolding.

## Sources
- `project-context/1.define/prd.md`
- `project-context/2.build/sad.md`
- `.cursor/templates/sad-template.md`
- `.cursor/agents/system-arch.md`

## Assumptions
- Team capacity aligns with PRD resource model.
- FastAPI + CrewAI stack is approved for this implementation.
- MVP timeline target remains 8-10 weeks.

## Open Questions
- Which candidate source integration is first priority for pilot users?
- What level of ATS export formatting is required for pilot go-live?
- Is asynchronous queue infrastructure required in MVP or can direct worker invocation suffice initially?

## Audit
- Timestamp: 2026-05-10
- Persona: `@system.arch`
- Action: Authored architecture implementation plan and execution status aligned to SAD and PRD.
