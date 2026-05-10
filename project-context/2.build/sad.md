# System Architecture Document (SAD)

## Document Control
- Product: Recruitment Assistant Application (TalentFlow AI)
- Version: 1.0
- Date: 2026-05-10
- Owner Persona: `@system.arch`
- Runtime: `crewai`
- Scope: MVP architecture for recruiter-facing candidate search, evaluation, and recommendation

## 1. MVP Architecture Philosophy & Principles

### MVP Design Principles
- Customer feedback first: deliver recruiter value quickly via candidate search, evaluation, and ranked shortlist.
- Keep architecture modular and simple: one frontend, one API service, one CrewAI worker, one operational datastore.
- Human-in-the-loop by default: recruiter approval gates remain mandatory for high-impact workflow outputs.
- Observable and auditable by design: stage logs, trace IDs, and explicit decision records at each agent handoff.

### Core vs Future Decision Framework
- **MVP (Phase 1)**: researcher/evaluator/recommender workflow, recruiter web interface, structured shortlist output, baseline telemetry.
- **Deferred (Future Work)**: full ATS bidirectional sync, candidate outbound communication automation, predictive quality-of-hire analytics.
- **Validation objective**: prove time-to-source improvement and shortlist relevance before scaling integrations and infrastructure complexity.

### Technical Architecture Decisions
- **Frontend selection**: simple web UI is selected over CLI for recruiter usability, onboarding speed, and shared review experience.
- **Backend selection**: FastAPI is selected over Flask for built-in validation, async support, and clearer API schema contracts.
- **Orchestration pattern**: CrewAI sequential process ensures deterministic stage ordering and reproducibility for MVP.
- **Response model**: synchronous request/response for short runs plus async job polling for longer candidate evaluation batches.

## 2. Multi-Agent System Specification

### Agent Architecture
- **`researcher_agent`**:
  - Goal: source candidate pool from role requirements and filter constraints.
  - Inputs: structured job requirements, optional constraints.
  - Outputs: candidate pool with evidence snippets and source metadata.
  - Tools: candidate source connectors, search utilities, profile extraction utility.
- **`evaluator_agent`**:
  - Goal: score candidates against configurable rubric.
  - Inputs: candidate pool + rubric criteria.
  - Outputs: normalized score, criteria-level rationale, confidence indicator.
  - Tools: rubric scorer, profile normalizer, confidence checker.
- **`recommender_agent`**:
  - Goal: rank and present shortlist recommendations.
  - Inputs: evaluated candidate set + ranking preferences.
  - Outputs: ranked shortlist, recommendation notes, uncertainty flags.
  - Tools: ranking engine, explanation formatter.

### Collaboration Pattern
- Process mode: **Sequential** (researcher -> evaluator -> recommender).
- Context passing contracts:
  - `researcher_agent -> evaluator_agent`: candidate id, source metadata, summary, role-fit evidence.
  - `evaluator_agent -> recommender_agent`: candidate id, normalized score, criteria rationale, confidence.
- Human checkpoints:
  - Retry/revise intake when candidate pool quality threshold fails.
  - Confirm rubric updates when evaluator confidence is low.
  - Approve final shortlist before hiring manager handoff.

### Task Orchestration and Runtime Controls
- Crew-level controls:
  - `max_iter <= 12`
  - `max_retry_limit >= 2`
  - crew `max_rpm` enforced for cost control
  - stage timeout defaults: researcher 90s, evaluator 180s, recommender 60s
- Idempotency:
  - `request_id` and `run_id` required for each run.
  - reruns overwrite stage artifacts for same run version and preserve audit trail.
- Failure policy:
  - retry stage up to 2 times for transient errors.
  - on repeated failure, halt run and return actionable error with preserved intermediate outputs.

### CrewAI Configuration
- Config files: `config/agents.yaml`, `config/tasks.yaml`.
- Runtime entrypoint: `crew.py`.
- Delegation: disabled for MVP agents (`allow_delegation: false`).
- Logging:
  - stage start/stop, retries, errors, token/cost estimates.
  - persisted lifecycle logs under `project-context/2.build/logs` for build traceability.

## 3. Frontend Architecture Specification

### Frontend Technology Stack (MVP)
- Web app: lightweight React + TypeScript single-page interface.
- UI: simple component library (forms, tables, badges, status toasts).
- State: minimal client state with request session persistence in local storage.
- Accessibility: keyboard navigation, semantic labels, and contrast-safe status indicators.

### UI Structure
- **Role Intake View**:
  - recruiter enters role title, must-have skills, preferred skills, experience, location.
  - validation blocks incomplete critical fields.
- **Run Monitor View**:
  - shows stage status (`researching`, `evaluating`, `recommending`, `awaiting_approval`).
  - displays errors with retry and resume actions.
- **Recommendation View**:
  - ranked shortlist table with fit score and rationale.
  - side panel for candidate details and criteria breakdown.
- **Review Actions**:
  - approve, revise constraints, rerun from researcher, rerun from evaluator.

### Interaction Design and Error UX
- Real-time status polling every 2-5 seconds for active run updates.
- Explicit low-confidence warnings and recommendation uncertainty flags.
- Clear fallback actions for no candidates found, timeout, and integration failures.
- Export action for approved shortlist payload in structured JSON/CSV.

## 4. Backend Architecture Specification

### API Architecture (FastAPI)
- Core endpoints:
  - `POST /api/v1/runs` create recruitment workflow run.
  - `GET /api/v1/runs/{run_id}` fetch run status + stage outputs.
  - `POST /api/v1/runs/{run_id}/rerun` rerun from stage with updated parameters.
  - `POST /api/v1/runs/{run_id}/approve` approve and finalize shortlist.
  - `GET /api/v1/health` health/readiness check.
- Validation:
  - Pydantic schemas for all request/response payloads.
  - strict enum/state constraints for run lifecycle transitions.
- Security:
  - API key or bearer auth for MVP.
  - role claims support for recruiter/hiring-manager/admin.
  - input sanitization and payload size limits.

### Data Architecture
- MVP datastore: PostgreSQL (single instance) for run state and audit data.
- Core entities:
  - `requisition`, `workflow_run`, `stage_result`, `candidate_profile`, `evaluation_score`, `recommendation`, `audit_event`.
- Retention:
  - active workflow data retained for product analytics and audit.
  - soft-delete policy with planned GDPR deletion workflow in later phase.

### CrewAI Integration Layer
- API service invokes CrewAI orchestration module through internal service boundary:
  - `run_research_stage()`
  - `run_evaluation_stage()`
  - `run_recommendation_stage()`
- Stage output schema normalization occurs before persistence and response.
- Graceful degradation:
  - if source connector unavailable, return partial manual-import pathway.

### Error Handling and Observability
- Standardized error envelope:
  - `error_code`, `message`, `retryable`, `suggested_action`, `trace_id`.
- Structured logs include:
  - `trace_id`, `run_id`, `stage`, latency, retries, outcome.
- Metrics:
  - stage success rate, run completion time, shortlist acceptance rate.

## 5. DevOps & Deployment Architecture

### Environments
- Local development, staging, production with environment-scoped secrets.
- Runtime secrets managed via environment variables (`.env`/secret manager in deployed env).

### Container and Deployment
- Services:
  - `frontend-web` container (serves static assets + API proxy config as needed).
  - `backend-api` container (FastAPI).
  - `crew-worker` container (CrewAI runtime).
  - `postgres` managed service.
- MVP deployment target:
  - cloud VM/container platform with autoscaling disabled initially (manual scaling).

### CI/CD
- Pipeline stages:
  - lint + unit tests
  - integration tests for API/crew contract
  - build container images
  - deploy to staging
  - smoke tests
  - promote to production
- Rollback:
  - prior image tag redeploy + schema-compatible migration policy.

### Monitoring
- Centralized logs and dashboards for API latency, stage failures, and run throughput.
- Alerting:
  - repeated stage failures
  - run timeout spikes
  - API error rate threshold breach.

## 6. Data Flow & Integration Architecture

### End-to-End Request Flow
1. Recruiter submits role requirements from web UI.
2. Frontend calls `POST /runs`, receives `run_id`.
3. Backend starts sequential crew execution and persists stage artifacts.
4. Frontend polls run status and renders stage outputs incrementally.
5. Recruiter reviews shortlist and approves or requests rerun.
6. Backend finalizes approved recommendation package for manager review.

### Integration Points
- Candidate source connectors (MVP may include file import + one external source).
- ATS integration boundary:
  - outbound shortlist payload endpoint placeholder for future bidirectional sync.
- Optional notifications:
  - email/webhook on run completion or approval.

### Data Contracts
- Candidate profile contract:
  - `candidate_id`, `name`, `skills`, `experience`, `location`, `source`, `evidence`.
- Evaluation contract:
  - `candidate_id`, `score_normalized`, `criteria_scores`, `rationale`, `confidence`.
- Recommendation contract:
  - `candidate_id`, `rank`, `recommendation_note`, `uncertainty_flag`.

## 7. Performance & Scalability Specifications

### Performance Targets (MVP)
- P95 synchronous API response (non-crew endpoints): <= 2.5s.
- Candidate evaluation batch (200 candidates): <= 10 minutes.
- Stage retry overhead bounded by timeout and retry limits.

### Scalability Path
- Horizontal scale:
  - split API and worker process pools as load grows.
- Queue introduction trigger:
  - when active concurrent runs consistently exceed single-worker capacity.
- Data scaling:
  - add read replicas and partition stage logs once retention volume increases.

### Resource Optimization
- Cache static rubric templates and role taxonomies in memory.
- Deduplicate repeated candidate profile parsing per run.
- Track token and API usage per stage for budget governance.

## 8. Security & Compliance Architecture

### Security Controls
- TLS for all service-to-service and client-to-server traffic.
- Encryption at rest for database and backups.
- Least-privilege credentials for connectors and internal services.
- Input validation and output escaping on all user-generated fields.

### Privacy and Responsible AI
- No protected attributes used directly in scoring decisions.
- Decision traceability with evidence and rationale for each recommendation.
- Role-based access controls:
  - recruiters can run/edit workflows.
  - hiring managers can view approved shortlist.
  - admins manage configuration and audits.

### Compliance Readiness
- Audit logs for high-impact actions (approval, rerun, export).
- Data retention/deletion policy placeholders aligned with GDPR-ready roadmap.
- Secret management via environment variables only; no hardcoded credentials.

## 9. Testing & Quality Assurance Specifications

### Testing Strategy
- Unit tests:
  - request schema validation
  - stage scoring logic
  - recommendation ranking constraints
- Integration tests:
  - FastAPI <-> CrewAI orchestration contract
  - persistence of stage outputs and retry behavior
- End-to-end tests:
  - recruiter intake -> run -> review -> approve flow
  - rerun flow on low-confidence or low-pool-quality scenarios

### Quality Gates
- Lint and tests required before staging deploy.
- Contract tests for handoff payload schemas between agents.
- Smoke tests for health endpoint, run creation, and status retrieval.
- Manual UAT checklist for rationale quality and recruiter decision controls.

## 10. MVP Launch & Feedback Strategy

### Pilot Rollout
- Pilot cohort: 3-5 recruiter teams.
- Controlled usage with weekly KPI review.
- Feedback channels:
  - in-app thumbs-up/down on shortlist quality
  - structured weekly qualitative interviews.

### Success Metrics
- Time-to-source reduction >= 25% in pilot.
- Shortlist relevance >= 75% hiring manager satisfaction baseline.
- Run success rate >= 98% for core flow.
- Recruiter satisfaction >= 4.0/5 for pilot go-forward threshold.

### Iteration Strategy
- Weekly release cadence for workflow quality and UX fixes.
- Prioritize reliability and explainability defects before feature expansion.
- Promote deferred integrations/features only after MVP KPI thresholds hold for 8 consecutive weeks.

## Traceability Matrix (PRD -> Architecture Components)
- FR-0 Candidate Search -> `researcher_agent`, role intake UI, candidate source integration boundary.
- FR-2 Candidate Screening -> `evaluator_agent`, rubric engine, evaluation contract and score persistence.
- FR-3 Ranked Recommendations -> `recommender_agent`, recommendation view, approval workflow endpoint.
- FR-4 Dashboard visibility (MVP-lite) -> run monitor view, stage telemetry metrics, audit events.
- NFR Performance/Reliability -> FastAPI async model, retry policy, timeout controls, monitoring/alerts.
- Security/Compliance requirements -> RBAC boundaries, audit logs, encryption policies, protected-attribute exclusion controls.

## Future Work
- Full ATS read/write synchronization with conflict resolution workflows.
- Candidate communication automation with compliant templates and scheduling.
- Advanced analytics dashboards and predictive quality-of-hire signals.
- SSO integration and enterprise security controls.
- Expanded geographies and policy packs for region-specific compliance.

## Sources
- `project-context/1.define/prd.md`
- `.cursor/templates/sad-template.md`
- `.cursor/agents/system-arch.md`

## Assumptions
- MVP uses web UI as primary interface; CLI is optional developer utility and not primary user channel.
- FastAPI is approved runtime for backend API in this build phase.
- Candidate source connectors are available through at least one usable integration path or import mechanism.
- Recruiter approval remains mandatory before shortlist sharing.

## Open Questions
- Which initial external candidate source is prioritized for MVP (LinkedIn-like source, ATS export, or internal DB)?
- Should shortlist export target a specific ATS format in MVP or remain generic JSON/CSV?
- What confidence threshold values should trigger mandatory rerun vs optional review?
- Is fine-grained role permissioning needed in MVP beyond recruiter/hiring-manager/admin?

## Audit
- Timestamp: 2026-05-10
- Persona: `@system.arch`
- Action: Created comprehensive MVP SAD for Recruitment Assistant using CrewAI sequential architecture, simple web frontend, FastAPI backend, and explicit integration/control contracts.
- Runtime Resolution: `AAMAD_TARGET_RUNTIME=crewai` (default per project context and PRD).
