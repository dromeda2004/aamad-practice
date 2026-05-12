# Deployment Plan — TalentFlow AI MVP

## Document Control
- Product: Recruitment Assistant Application (TalentFlow AI)
- Version: 1.0
- Date: 2026-05-11
- Owner Persona: `@devops-eng`
- Status: **In Progress** — Deployment configurations being finalized

## 1. Deployment Overview

### MVP Deployment Strategy
**Approach:** Docker containerization with docker-compose for local/staging and container registry for production.

**Key Principles:**
- Minimal infrastructure footprint for MVP (no managed database, load balancer, or orchestration cluster)
- Fast iteration cycle supporting frequent validation and hotfixes
- Clear separation between development and production configurations
- Deterministic reproducibility via containerization

### Deployment Options
1. **Local Development**: Native Python + Node.js with environment variables
2. **Local Containerized**: docker-compose with separate backend and frontend containers
3. **Staging/Production**: Container images pushed to registry (ECR, Docker Hub, or Artifact Registry)

## 2. Deployment Approach

### Local Development (No Docker)
**Use case**: Developer laptops, CI/CD testing.

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export USE_MOCK_CREW=true
export API_KEY=dev-key-123
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Vite dev server on http://localhost:5173
```

**Access:** http://localhost:5173 (frontend automatically proxies /api to localhost:8000)

### Local Containerized (Docker Compose)
**Use case**: Staging validation, integration testing, team onboarding.

**Files:**
- `Dockerfile.backend` — Backend service image
- `Dockerfile.frontend` — Frontend build artifact image
- `docker-compose.yml` — Orchestration for both services
- `.env.docker` — Environment variables for containerized deployment

**Launch:**
```bash
docker-compose up -d
```

**Access:** http://localhost:80 or http://localhost:3000 (reverse proxy or direct)

### Cloud/Production (Container Registry + Orchestration)
**Use case**: Pilot deployment, production release.

**Deployment Flow:**
1. Push backend and frontend images to container registry (ECR, Docker Hub, Artifact Registry)
2. Tag images with version/commit SHA
3. Deploy backend service with environment variables (OPENAI_API_KEY, etc.)
4. Deploy frontend service or static content to CDN/S3
5. Configure API gateway/load balancer if needed for HA

**Environment Setup:**
- Production `.env` file with secrets managed via environment variables or secrets manager
- CORS configuration for production frontend domain
- API key or OAuth2 authentication enabled

## 2b. Deployment Artifacts

### Files Created
- **`Dockerfile.backend`** — Multi-stage build for FastAPI + CrewAI backend
  - Base: Python 3.11-slim
  - Builds dependencies in isolated layer
  - Exposes port 8000
  - Health check via `/api/v1/health` endpoint
  - Runs: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

- **`Dockerfile.frontend`** — Multi-stage build for React + Vite frontend
  - Build stage: Node 20-alpine + npm ci + npm run build
  - Runtime stage: Node 20-alpine + serve (lightweight static server)
  - Exposes port 3000
  - Health check via wget on root endpoint
  - Runs: `serve -s dist -l 3000`

- **`docker-compose.yml`** — Service orchestration
  - `backend` service (port 8000, depends on health)
  - `frontend` service (port 3000, depends on backend health)
  - `talentflow-network` bridge network
  - Shared environment variables
  - Health checks on both services
  - Volume mounts for development (optional)

- **`.env.docker`** — Environment variables template
  - Backend config (API host, port, CrewAI settings)
  - Frontend config (API base URL)
  - Security settings (API key, CORS origins)
  - Logging and monitoring flags

- **`deploy.sh`** — Automated deployment script
  - Accepts environment (staging|production) and version
  - Builds images
  - Validates locally with docker-compose
  - Runs health checks and smoke tests
  - Provides rollback instructions

- **`rollback.sh`** — Rollback automation
  - Stops services
  - Pulls previous version images
  - Restarts with previous version
  - Verifies health

- **`health-check.sh`** — Health check utility
  - Tests backend `/api/v1/health`
  - Tests frontend root endpoint
  - Runs smoke test (creates a run)
  - Color-coded output

## 3. Required Dependencies and Environment Setup

### Backend Dependencies
**Runtime:** Python 3.10+ (3.11+ recommended)

**Required packages:**
```
fastapi>=0.115
uvicorn[standard]>=0.32
pydantic>=2,<3
pyyaml>=6
python-dotenv>=1
crewai>=0.76
```

**Optional (for LLM execution):**
```
openai>=1.0  # for CrewAI LLM fallback
aiofiles>=23.0  # for async file operations
```

### Frontend Dependencies
**Runtime:** Node.js 18+ (20+ recommended), npm 9+

**Required packages:**
```
react ^18.3.1
react-dom ^18.3.1
vite ^5.4.11
typescript ~5.6.3
```

### System Requirements
- **Disk space**: 2GB minimum (Python packages + node_modules + build artifacts)
- **Memory**: 1GB minimum (backend), 512MB minimum (frontend)
- **Network**: Outbound HTTPS for OpenAI API (if using real crew)

## 4. Configuration Requirements

### Environment Variables

#### Backend (.env)
```bash
# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# CrewAI Configuration
USE_MOCK_CREW=true  # Set to false for real LLM execution
CREW_MODEL=gpt-4
CREW_MAX_RPM=10
CREW_MAX_ITER=12

# LLM API Keys (required if USE_MOCK_CREW=false)
OPENAI_API_KEY=sk-...
# OR
AZURE_OPENAI_KEY=...

# Security (MVP stub)
API_KEY=dev-key-123

# CORS (for frontend origin)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: Enable structured logging
ENABLE_JSON_LOGS=false
TRACE_ID_ENABLED=true
```

#### Frontend (.env)
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000  # Leave empty for dev proxy
VITE_API_TIMEOUT_MS=30000

# Optional: Analytics or feature flags
VITE_DEMO_MODE=false
```

### Docker Configuration (.env.docker)
```bash
# Backend service
BACKEND_IMAGE=talentflow-backend:latest
BACKEND_PORT=8000
USE_MOCK_CREW=true
API_KEY=prod-key-secure

# Frontend service
FRONTEND_IMAGE=talentflow-frontend:latest
FRONTEND_PORT=3000

# Shared
LOG_LEVEL=info
```

## 5. Deployment Steps

### Pre-Deployment Validation
1. **Code review**: All changes merged and tested locally
2. **Build testing**: `npm run build` (frontend) succeeds without errors
3. **Unit tests**: Backend health check endpoint responds
4. **Integration tests**: End-to-end workflow (intake → research → eval → recommend) completes
5. **Security scan**: Docker images scanned for CVEs (if using container registry)

### Deployment Checklist

#### Step 1: Build Container Images
```bash
# Backend image
docker build -f Dockerfile.backend -t talentflow-backend:latest .

# Frontend image (build React, then serve static)
docker build -f Dockerfile.frontend -t talentflow-frontend:latest .

# Verify images
docker images | grep talentflow
```

#### Step 2: Local Validation (docker-compose)
```bash
# Start services
docker-compose -f docker-compose.yml up -d

# Health check backend
curl http://localhost:8000/api/v1/health

# Verify frontend is accessible
curl -s http://localhost:3000 | head -c 200

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Step 3: Tag and Push (if using registry)
```bash
# Tag for registry
docker tag talentflow-backend:latest <registry>/talentflow-backend:v1.0.0
docker tag talentflow-frontend:latest <registry>/talentflow-frontend:v1.0.0

# Push
docker push <registry>/talentflow-backend:v1.0.0
docker push <registry>/talentflow-frontend:v1.0.0
```

#### Step 4: Deploy to Staging/Production
```bash
# Option A: docker-compose on dedicated host
ssh deploy@staging-host
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Option B: Kubernetes (future)
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

#### Step 5: Post-Deployment Validation
```bash
# Health check
curl https://staging.talentflow.ai/api/v1/health

# Smoke test: Create a run
curl -X POST https://staging.talentflow.ai/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "requisition": {
      "role_title": "Senior Backend Engineer",
      "must_have_skills": ["Python", "FastAPI"],
      "preferred_skills": ["CrewAI"],
      "experience_min_years": 5,
      "experience_max_years": 10,
      "location": "Remote",
      "employment_type": "full-time",
      "free_text_brief": ""
    }
  }'

# Verify run proceeds through stages (poll every 2s)
curl https://staging.talentflow.ai/api/v1/runs/{run_id}
```

## 6. Rollback Procedures

### Immediate Rollback (Failed Deployment)
**Scenario:** New version crashes immediately after deployment.

**Steps:**
1. Stop current container: `docker-compose down`
2. Restore previous version tag from registry
3. Redeploy previous version: `docker-compose up -d`
4. Verify health: `curl /api/v1/health`

**Time estimate:** 2-5 minutes

### Gradual Rollback (Performance Degradation)
**Scenario:** New version passes initial tests but fails under load or causes memory leaks.

**Steps:**
1. Check container resource usage: `docker stats`
2. Review logs for errors: `docker-compose logs backend | tail -n 100`
3. If confirmed bad release, execute immediate rollback above
4. File incident and conduct root cause analysis

**Time estimate:** 5-15 minutes (diagnosis) + 2-5 minutes (execution)

### Data Rollback (Data Corruption)
**Scenario:** Schema migration or data processing error corrupts state.

**Note:** MVP uses in-memory storage, so no persistent data rollback needed. Run state is ephemeral and resets on container restart.

**Steps:**
1. Stop container
2. Restart container (forces clean state)
3. Alert users to resubmit any in-flight runs

## 7. Status Tracking

### Deployment Progress

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| Dockerfile.backend | ✅ Completed | @devops-eng | Multi-stage Python 3.11 build with health checks |
| Dockerfile.frontend | ✅ Completed | @devops-eng | Node 20 build + serve static files on port 3000 |
| docker-compose.yml | ✅ Completed | @devops-eng | Orchestrates backend + frontend with networking |
| .env.docker | ✅ Completed | @devops-eng | Environment configuration template |
| deploy.sh | ✅ Completed | @devops-eng | Automated build, validate, and smoke test |
| rollback.sh | ✅ Completed | @devops-eng | Rollback to previous version with verification |
| health-check.sh | ✅ Completed | @devops-eng | Health check and smoke test utility |
| Health check validation | In Progress | QA/DevOps | Manual testing of all endpoints |
| Staging deployment | Pending | DevOps | Cloud/host setup and configuration |
| Production readiness checklist | Pending | DevOps/Product | Go/no-go gate |

### Key Milestones
- **M1 (2026-05-11):** Dockerfile + docker-compose completed and tested locally
- **M2 (2026-05-12):** Staging environment online and validated
- **M3 (2026-05-13):** Production readiness checklist signed off
- **M4 (2026-05-14):** Soft launch to pilot users with monitoring

## 8. Production Readiness Checklist

### Infrastructure
- [ ] Hosting environment (Docker host, Kubernetes cluster, or serverless) configured
- [ ] Network connectivity (ingress, egress, CORS) configured
- [ ] Storage (if needed) provisioned and tested
- [ ] Backup/recovery procedures documented

### Security
- [ ] Secrets (API keys, credentials) stored securely (not in code)
- [ ] CORS policy restricted to production frontend domain
- [ ] API key authentication enabled
- [ ] Container images scanned for vulnerabilities
- [ ] Network policies restrict unnecessary traffic

### Monitoring & Observability
- [ ] Health check endpoint monitored (alerting on failure)
- [ ] Error logging enabled and searchable
- [ ] Trace IDs propagated for debugging
- [ ] Resource usage (CPU, memory) monitored
- [ ] Run success/failure rates tracked

### Documentation
- [ ] Deployment runbook written and reviewed
- [ ] Rollback procedures documented and tested
- [ ] Incident response plan created
- [ ] Operational runbooks for common tasks (scale, redeploy, debug)

### Load & Performance
- [ ] Load testing completed (target: 10 concurrent runs)
- [ ] Timeout behavior verified (90s researcher, 180s evaluator, 60s recommender)
- [ ] Memory footprint under load acceptable
- [ ] API response times within SLA (target: <2s for non-crew endpoints)

### Testing
- [ ] Smoke tests pass (health check + end-to-end run)
- [ ] Integration tests pass (all API endpoints)
- [ ] Rollback tested (manual or automated)
- [ ] Failure scenarios tested (no crew, timeout, invalid input)

## 9. Known Limitations & Future Improvements

### MVP Limitations
- **No persistent storage:** Runs are in-memory only; will be lost on restart
- **No HA/redundancy:** Single-instance only; no failover
- **No scaling:** Synchronous CrewAI execution blocks on LLM calls
- **No advanced monitoring:** Basic health checks only; no observability platform
- **No CI/CD automation:** Manual deployment; no automated rollout pipeline

### Future Enhancements (Post-MVP)
- PostgreSQL persistence and migrations
- Kubernetes deployment with auto-scaling
- Async job queue (Celery/RQ) for long-running crew tasks
- Prometheus metrics + Grafana dashboards
- GitHub Actions CI/CD pipeline with automated testing and deployment
- Helm charts for Kubernetes
- Multi-region failover and load balancing

## Sources
- `project-context/1.define/prd.md`
- `project-context/2.build/sad.md`
- `project-context/2.build/backend.md`
- `project-context/2.build/frontend.md`
- `project-context/2.build/integration-plan.md`

## Audit
- Timestamp: 2026-05-11
- Persona: `@devops-eng`
- Action: Created deployment plan, Dockerfiles, docker-compose.yml, and automation scripts. Local validation via docker-compose in progress.
- Status: MVP deployment artifacts complete. Ready for staging validation.
