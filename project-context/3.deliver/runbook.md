# TalentFlow AI Recruitment Assistant — Operations Runbook

## Document Control
- **Product**: TalentFlow AI Recruitment Assistant
- **Version**: 1.0
- **Date**: 2026-05-17
- **Owner Persona**: `@devops-eng`
- **Status**: Production Ready (MVP)
- **Last Updated**: 2026-05-17

---

## 1. Application Overview

### What is TalentFlow AI?

TalentFlow AI is a CrewAI-powered multi-agent recruitment assistant that automates candidate sourcing, evaluation, and ranking. It provides recruiters and hiring managers with a streamlined workflow to:

1. **Research** — Source and discover candidate pools based on job requirements
2. **Evaluate** — Score candidates against role-specific criteria
3. **Recommend** — Deliver ranked shortlists with fit scores and confidence signals
4. **Approve** — Enable recruiter review and approval before recruiter/hiring manager handoff

### Architecture Summary

- **Frontend**: React + TypeScript web UI (Vite)
- **Backend**: FastAPI async API service with structured logging
- **Runtime**: CrewAI orchestration (researcher, evaluator, recommender agents)
- **Data Store**: In-memory SQLite for MVP (can be upgraded to PostgreSQL)
- **Observability**: Structured JSON logs, CrewAI tracing, health checks

### Key Features

- Multi-stage async candidate evaluation workflow
- Trace ID correlation across request → pipeline → agent logs
- Configurable crew mode (mock for development, real LLM for production)
- Stage rerun/resume capability for iterative refinement
- Built-in health monitoring and error recovery

---

## 2. Prerequisites and Dependencies

### System Requirements

- **Operating System**: Linux, macOS, or Windows (WSL2 recommended)
- **Python**: 3.10 or 3.11 (3.13 not yet tested)
- **Node.js**: 18.x or 20.x (for frontend)
- **Disk**: 2 GB minimum (includes dependencies and logs)
- **Memory**: 4 GB minimum (8+ GB recommended for LLM crew mode)

### Required Software

```bash
# Check Python version
python --version
# Output: Python 3.11.x

# Check Node.js version
node --version
# Output: v20.x.x or v18.x.x

# Check npm
npm --version
# Output: 10.x.x or 9.x.x
```

### Required Environment Variables (Core)

For **all** deployments, set these:

- `OPENAI_API_KEY` — OpenAI API key (if using real LLM crew)
- `API_KEY` — (Optional) API authentication key for endpoint security
- `ENVIRONMENT` — `development` or `production`

For **development** only:

- `USE_MOCK_CREW=true` — Use deterministic mock agents instead of LLM

For **production** only:

- `USE_MOCK_CREW=false` — Use real CrewAI with LLM
- `CREWAI_TRACING_ENABLED=true` — Enable CrewAI AOP tracing
- `CREW_AOP_API_KEY=<secret>` — CrewAI tracing API key
- `LOG_FORMAT=json` — Structured JSON logging
- `LOG_FILE_PATH=/var/log/talentflow` — Persistent log directory

---

## 3. Installation Instructions

### 3.1 Local Development Setup (Native Python + Node.js)

#### Step 1: Clone and navigate to repo

```bash
git clone <repo-url>
cd d:\aamad\test  # or your repo path
```

#### Step 2: Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

If you encounter issues, create a virtual environment first:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Install frontend dependencies

```bash
cd ../frontend
npm install
```

#### Step 4: Verify installations

```bash
# Backend
python --version
pip list | grep crewai
pip list | grep fastapi

# Frontend
npm list react
npm list typescript
```

### 3.2 Docker Containerized Setup (Development & Staging)

#### Prerequisites

- Docker Desktop installed and running
- docker-compose v2+

#### Step 1: Verify Docker setup

```bash
docker --version
docker-compose --version
```

#### Step 2: Build images

```bash
cd /path/to/repo
docker-compose build
```

#### Step 3: Launch services

```bash
docker-compose up -d
docker-compose ps
```

Expected output:

```
NAME            COMMAND              SERVICE     STATUS      PORTS
backend         "uvicorn app.main"   backend     Up          0.0.0.0:8000->8000/tcp
frontend        "serve -s dist"      frontend    Up          0.0.0.0:3000->3000/tcp
```

---

## 4. Configuration

### 4.1 Environment Variables

Create a `.env` file in the `backend/` folder (`.env.example` provided):

#### Minimal Development

```bash
# backend/.env
ENVIRONMENT=development
USE_MOCK_CREW=true
LOG_LEVEL=INFO
LOG_FORMAT=text
CREWAI_TELEMETRY_OPT_OUT=true
```

#### Full Production

```bash
# backend/.env
ENVIRONMENT=production
USE_MOCK_CREW=false
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=/var/log/talentflow
CREWAI_TRACING_ENABLED=true
CREW_AOP_API_KEY=<your-secret-api-key>
OPENAI_API_KEY=<your-openai-key>
API_KEY=<optional-auth-key>
CREW_MAX_RPM=10
CREW_MAX_ITER=12
CREWAI_TELEMETRY_OPT_OUT=true
```

### 4.2 CrewAI Configuration

Agent and task definitions are externalized in YAML:

- **Agents**: `backend/config/agents.yaml`
  - `researcher` — Candidate sourcing role
  - `evaluator` — Fit scoring role
  - `recommender` — Ranking and recommendation role

- **Tasks**: `backend/config/tasks.yaml`
  - `research_task` — Generate candidate pool
  - `evaluate_task` — Score candidates
  - `recommend_task` — Rank and recommend

To customize:

```yaml
# backend/config/agents.yaml
agents:
  researcher:
    role: "Candidate Sourcing Specialist"
    goal: "Source qualified candidates from structured job requirements"
    backstory: "Expert at..."
    allow_delegation: false

# backend/config/tasks.yaml
tasks:
  research_task:
    description: "Search and source candidates..."
    expected_output: "Candidate pool JSON with skills matched..."
```

### 4.3 Frontend Configuration

Frontend connects to backend via environment variable (`.env.local` in `frontend/`):

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

For production, update to your API endpoint:

```bash
# frontend/.env.production
VITE_API_URL=https://api.yourdomain.com
```

---

## 5. How to Run the Application

### 5.1 Development Mode (Local, No Docker)

#### Terminal 1: Backend

```bash
cd backend
export USE_MOCK_CREW=true  # or set in .env
export LOG_LEVEL=INFO
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process [12345]
[timestamp] INFO Application startup complete
```

#### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

Expected output:

```
VITE v5.x.x build ready in Xs

➜  Local:   http://localhost:5173/
```

#### Access the application

Open browser to `http://localhost:5173`

### 5.2 Containerized Mode (Docker Compose)

```bash
# From repo root
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

Access application at `http://localhost:3000` or `http://localhost:80`

### 5.3 Production Mode

#### Using environment variables

```bash
cd backend
export ENVIRONMENT=production
export LOG_FORMAT=json
export LOG_FILE_PATH=/var/log/talentflow
export CREWAI_TRACING_ENABLED=true
export CREW_AOP_API_KEY=<secret>
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Docker

```bash
docker build -f Dockerfile.backend -t talentflow-backend:1.0 .
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_FORMAT=json \
  -e CREWAI_TRACING_ENABLED=true \
  -e CREW_AOP_API_KEY=<secret> \
  --name talentflow-backend \
  talentflow-backend:1.0
```

---

## 6. How to Monitor and View Logs

### 6.1 Development Logs (Console)

Backend logs appear in the terminal where uvicorn is running:

```
[2026-05-17 10:30:45] INFO: Request start (request_id=abc123, method=POST, path=/api/v1/runs)
[2026-05-17 10:30:46] INFO: Pipeline start (run_id=run-001, trace_id=trace-001, stage=researching)
[2026-05-17 10:30:47] INFO: Using mock crew (crew_stage=research, use_mock=true)
[2026-05-17 10:30:48] INFO: agent complete (stage=researching, agent=researcher)
[2026-05-17 10:31:00] INFO: Request complete (request_id=abc123, status_code=200, duration_ms=15000)
```

### 6.2 Production Logs (File-Based)

Logs are written to `/var/log/talentflow/app.log` and `/var/log/talentflow/error.log`:

#### View logs in real-time

```bash
tail -f /var/log/talentflow/app.log
```

#### Search logs by trace ID

```bash
grep "trace_id=trace-001" /var/log/talentflow/app.log
```

#### Parse JSON logs with jq

```bash
tail -100 /var/log/talentflow/app.log | jq -r '.timestamp, .level, .message, .run_id'
```

#### Filter by level

```bash
grep "ERROR" /var/log/talentflow/app.log
grep "WARNING" /var/log/talentflow/app.log
```

### 6.3 CrewAI Traces (Dashboard)

#### Enable tracing

```bash
export CREWAI_TRACING_ENABLED=true
export CREW_AOP_API_KEY=<your-key>
crewai login  # Authenticate with CrewAI AOP
```

#### View traces online

1. Visit `https://app.crewai.com`
2. Log in to your CrewAI account
3. Navigate to your project dashboard
4. Open the `Traces` tab to see:
   - Agent decision-making process
   - Task execution timeline
   - Tool usage and results
   - LLM call performance
   - Error occurrences

#### List traces via CLI

```bash
crewai traces list
crewai traces show <trace-id>
```

### 6.4 Key Log Events to Watch

| Event | Log Message | Meaning |
|-------|-------------|---------|
| **App Start** | `Application startup complete` | Backend is ready to accept requests |
| **Request Received** | `Request start` | HTTP request received, processing started |
| **Pipeline Start** | `Pipeline start` | Crew workflow is executing |
| **Agent Execution** | `agent start` / `agent complete` | Individual agent is running |
| **Crew Mode** | `Using mock crew` / `Using LLM crew` | Mock vs real LLM selection |
| **Run Created** | `Run created` | New workflow run initialized with `run_id` and `trace_id` |
| **Pipeline Complete** | `pipeline complete` | All agents completed, results ready |
| **Request Complete** | `Request complete` | HTTP response sent, request finished |
| **Error** | `Request failed` / `pipeline complete` (with error) | Error occurred, check error details |

---

## 7. Common Issues and Troubleshooting

### Issue 1: Backend fails to start with `ModuleNotFoundError: No module named 'app'`

**Root Cause**: Python is not running from the `backend/` directory.

**Solution**:

```bash
# ❌ Wrong
cd d:\aamad\test
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# ✅ Correct
cd d:\aamad\test\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

### Issue 2: API returns 422 Unprocessable Content

**Root Cause**: Request body doesn't match expected schema.

**Solution**: Verify the request includes `must_have_skills` (not `skills`):

```json
{
  "requisition": {
    "role_title": "Product Manager",
    "must_have_skills": ["AI", "product", "data"],
    "location": "Remote"
  }
}
```

Valid request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"requisition":{"role_title":"PM","must_have_skills":["AI","product","data"]}}'
```

---

### Issue 3: Frontend cannot connect to backend

**Root Cause**: CORS policy or backend not running on expected port.

**Solution**:

1. Verify backend is running:
   ```bash
   curl http://127.0.0.1:8000/api/v1/health
   # Expected: {"status":"ok"}
   ```

2. Check frontend VITE_API_URL in `.env.local`:
   ```bash
   # frontend/.env.local
   VITE_API_URL=http://localhost:8000
   ```

3. Restart frontend:
   ```bash
   npm run dev
   ```

---

### Issue 4: CrewAI tracing not appearing in dashboard

**Root Cause**: Tracing not enabled or authentication failed.

**Solution**:

1. Verify environment variables:
   ```bash
   echo $CREWAI_TRACING_ENABLED  # Should be "true"
   echo $CREW_AOP_API_KEY        # Should be set (but don't print in logs)
   ```

2. Authenticate with CrewAI:
   ```bash
   crewai login
   ```

3. Check backend logs for trace initialization:
   ```bash
   grep "tracing" /var/log/talentflow/app.log
   ```

4. If traces still don't appear, verify `backend/crew.py` has `tracing=True` enabled in Crew construction.

---

### Issue 5: Logs are not being written to `/var/log/talentflow/`

**Root Cause**: Directory doesn't exist or lacks write permissions.

**Solution**:

```bash
# Create directory with write permissions
sudo mkdir -p /var/log/talentflow
sudo chmod 755 /var/log/talentflow
sudo chown $(whoami):$(whoami) /var/log/talentflow

# Verify
ls -la /var/log/talentflow/
```

---

### Issue 6: Recommendation signal always shows "Low confidence"

**Root Cause**: Mock crew recommendation logic sets all uncertainty to True.

**Solution**: This is now fixed in `backend/app/mock_crew.py`. The `uncertain` flag is set based on evaluator confidence:

```python
# High confidence → False (Stable)
# Medium/Low confidence → True (Low confidence)
uncertain = row.get("confidence") != "high"
```

Restart backend to apply the fix.

---

### Issue 7: Docker image build fails with `pip install` errors

**Root Cause**: Missing dependencies or network issues.

**Solution**:

```bash
# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache

# Check pip in container
docker run --rm talentflow-backend:1.0 pip list
```

---

## 8. How to Stop and Restart the Application

### Local Development (Native)

#### Stop

```bash
# In the terminal running the backend:
# Press Ctrl+C

# In the terminal running the frontend:
# Press Ctrl+C
```

#### Restart

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (in new terminal)
cd frontend
npm run dev
```

### Docker Compose

#### Stop

```bash
docker-compose stop
```

#### Restart

```bash
docker-compose start
```

#### Stop and remove containers

```bash
docker-compose down
```

### Production (Systemd Service)

#### Create a systemd service file

```bash
sudo nano /etc/systemd/system/talentflow-backend.service
```

```ini
[Unit]
Description=TalentFlow AI Backend
After=network.target

[Service]
Type=notify
User=talentflow
WorkingDirectory=/opt/talentflow/backend
Environment="ENVIRONMENT=production"
Environment="LOG_FORMAT=json"
ExecStart=/usr/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Manage the service

```bash
# Start
sudo systemctl start talentflow-backend

# Stop
sudo systemctl stop talentflow-backend

# Restart
sudo systemctl restart talentflow-backend

# View status
sudo systemctl status talentflow-backend

# View logs
sudo journalctl -u talentflow-backend -f
```

---

## 9. Health Checks

### 9.1 Backend Health Check

#### HTTP endpoint

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok"
}
```

#### With custom header (if API_KEY is set)

```bash
curl -H "X-API-Key: <your-api-key>" http://127.0.0.1:8000/api/v1/health
```

### 9.2 Frontend Health Check

```bash
curl http://127.0.0.1:5173/
```

Expected response: HTML page with status 200

### 9.3 End-to-End Health Check

#### Create a test run

```bash
curl -X POST http://127.0.0.1:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "requisition": {
      "role_title": "Test Role",
      "must_have_skills": ["test"],
      "location": "Remote"
    }
  }'
```

Expected response includes `run_id` and `trace_id`:

```json
{
  "run_id": "run-abc123",
  "trace_id": "trace-abc123",
  "stage": "pending",
  "error": null,
  "created_at": "2026-05-17T10:30:45Z"
}
```

#### Fetch run status

```bash
curl http://127.0.0.1:8000/api/v1/runs/run-abc123
```

Check that `stage` progresses through:

1. `pending` → `researching` → `evaluating` → `recommending` → `awaiting_approval` → `approved`

### 9.4 Monitoring Dashboard Checks

#### Backend metrics

- Request latency: All requests should complete within 30 seconds
- Error rate: Should be < 1% in normal conditions
- Log volume: Should be consistent unless debugging

#### CrewAI metrics (from dashboard)

- Agent execution time: researcher ~2s, evaluator ~3s, recommender ~1s
- Token usage: Should align with expected crew sizes
- Error traces: Should be zero unless testing error paths

---

## 10. Operational Runbook Checklist

### Daily Operations

- [ ] Check backend logs for errors: `tail -f /var/log/talentflow/app.log`
- [ ] Verify application availability: `curl http://localhost:8000/api/v1/health`
- [ ] Monitor request latency and error rates
- [ ] Check CrewAI dashboard for trace anomalies

### Weekly Operations

- [ ] Review log rotation and archival
- [ ] Validate database size and cleanup old runs (if needed)
- [ ] Check CrewAI API rate limits and token usage
- [ ] Review and update runbook based on operational learnings

### Monthly Operations

- [ ] Assess storage usage for logs and database
- [ ] Review and rotate secrets (OPENAI_API_KEY, CREW_AOP_API_KEY)
- [ ] Run load testing to validate performance assumptions
- [ ] Plan and test disaster recovery procedures

### Incident Response

#### Pipeline Failure

1. Fetch the run: `curl http://127.0.0.1:8000/api/v1/runs/{run_id}`
2. Check the error: `run.error.message`
3. View logs: `grep "trace_id={trace_id}" /var/log/talentflow/app.log`
4. Retry the run: `POST /api/v1/runs/{run_id}/rerun`

#### High Request Latency

1. Check backend resource usage: `top`, `df`, `free`
2. Review CrewAI rate limits: `CREW_MAX_RPM` setting
3. Check log volume for spike: `wc -l /var/log/talentflow/app.log`
4. Restart backend service if needed

#### Database Issues

1. Check database file: `ls -la /path/to/database.db`
2. Verify disk space: `df /var/lib`
3. Check for locks: `lsof /path/to/database.db`
4. Restart backend to reset connections

---

## 11. Reference Documentation

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/runs` | Create new run |
| `GET` | `/api/v1/runs/{run_id}` | Fetch run status and results |
| `POST` | `/api/v1/runs/{run_id}/rerun` | Rerun from specific stage |
| `POST` | `/api/v1/runs/{run_id}/approve` | Approve recommendations |

### Environment Variables Quick Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Deployment environment |
| `USE_MOCK_CREW` | `auto` | Use mock crew agents |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log output format (json/text) |
| `LOG_FILE_PATH` | `/var/log/talentflow` | Log file directory |
| `CREWAI_TRACING_ENABLED` | `false` | Enable CrewAI tracing |
| `CREW_AOP_API_KEY` | — | CrewAI tracing API key |
| `CREW_MAX_RPM` | `10` | CrewAI requests per minute limit |
| `CREW_MAX_ITER` | `12` | Max iterations per task |

### Useful Commands

```bash
# View recent logs with timestamps
tail -n 100 /var/log/talentflow/app.log | jq -r '.timestamp + " [" + .level + "] " + .message'

# Count errors
grep "ERROR" /var/log/talentflow/error.log | wc -l

# Search by run_id
grep "run_id=run-xyz" /var/log/talentflow/app.log

# Check service status
sudo systemctl status talentflow-backend

# View container logs
docker logs -f talentflow-backend

# Inspect database
sqlite3 /path/to/database.db ".tables"
```

---

## 12. Support and Escalation

### Getting Help

1. **Runbook** — This document covers most operational tasks
2. **Project Context** — See `project-context/` for PRD, SAD, deployment plan, and monitoring plan
3. **Code Comments** — Check source code for implementation details in `backend/app/` and `frontend/src/`
4. **CrewAI Docs** — https://docs.crewai.com/
5. **Team** — Reach out to @devops-eng or @backend.eng for assistance

### Known Limitations (MVP)

- In-memory SQLite database (upgrade to PostgreSQL for production HA)
- No built-in authentication (API_KEY is optional, add OAuth2 as needed)
- Mock crew mode only for development (real LLM required for production)
- No automatic horizontal scaling (deploy multiple backend instances behind load balancer)

### Future Work

- [ ] Add PostgreSQL support for scalable persistence
- [ ] Implement OAuth2 authentication
- [ ] Set up Kubernetes deployment manifests
- [ ] Add APM (Application Performance Monitoring) integration
- [ ] Implement automatic backup and disaster recovery

---

## Document History

| Date | Author | Version | Notes |
|------|--------|---------|-------|
| 2026-05-17 | @devops-eng | 1.0 | Initial comprehensive runbook |

---

**Last Updated**: 2026-05-17  
**Next Review**: 2026-06-17
