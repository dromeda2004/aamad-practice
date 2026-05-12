# Deployment Quick Start — TalentFlow AI

This guide walks you through deploying TalentFlow AI using Docker containers.

## Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Bash (for scripts)

## Option 1: Local Development (No Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
export USE_MOCK_CREW=true
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend (separate terminal)
```bash
cd frontend
npm install
npm run dev
```

**Access:** http://localhost:5173

## Option 2: Local Containerized (Docker Compose)

### Quick Start
```bash
# Make scripts executable
chmod +x deploy.sh health-check.sh rollback.sh

# Build and validate
./deploy.sh staging latest

# Run health check
./health-check.sh
```

### Manual Steps
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/api/v1/health

## Option 3: Production Deployment

### Prerequisites
1. Docker registry (Docker Hub, ECR, or Artifact Registry)
2. Hosting environment (VM, container service, or Kubernetes cluster)
3. Environment configuration (.env files)

### Steps

#### 1. Build and push images
```bash
export REGISTRY=docker.io/your-org

docker build -f Dockerfile.backend -t $REGISTRY/talentflow-backend:v1.0.0 .
docker build -f Dockerfile.frontend -t $REGISTRY/talentflow-frontend:v1.0.0 .

docker push $REGISTRY/talentflow-backend:v1.0.0
docker push $REGISTRY/talentflow-frontend:v1.0.0
```

#### 2. Deploy on target host
```bash
ssh deploy@production-host

# Pull latest images
docker pull $REGISTRY/talentflow-backend:v1.0.0
docker pull $REGISTRY/talentflow-frontend:v1.0.0

# Create docker-compose.prod.yml with production settings
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl https://your-domain.com/api/v1/health
```

#### 3. Monitor
```bash
docker-compose logs -f
docker stats
```

## Health Checks

### Automated Health Check
```bash
./health-check.sh http://localhost:8000 http://localhost:3000
```

### Manual Checks
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend health
curl http://localhost:3000

# Create a test run
curl -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "requisition": {
      "role_title": "Test Role",
      "must_have_skills": ["Testing"],
      "preferred_skills": ["Docker"],
      "experience_min_years": 1,
      "experience_max_years": 3,
      "location": "Remote",
      "employment_type": "full-time"
    }
  }'
```

## Rollback

If deployment fails or causes issues:

```bash
# Rollback to previous version
./rollback.sh v1.0.0-previous
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify Python dependencies
docker-compose exec backend pip list

# Test health endpoint
curl -v http://localhost:8000/api/v1/health
```

### Frontend won't load
```bash
# Check logs
docker-compose logs frontend

# Verify build artifacts
docker-compose exec frontend ls -la dist/

# Check port binding
netstat -an | grep 3000
```

### API connection failing
```bash
# Verify services are running
docker-compose ps

# Check network connectivity
docker network inspect talentflow_talentflow-network

# Test from frontend container
docker-compose exec frontend curl http://backend:8000/api/v1/health
```

## Configuration

### Environment Variables
See `.env.docker` for all available configuration options.

**Key variables:**
- `USE_MOCK_CREW` — Use mock agents (true) or real OpenAI (false)
- `OPENAI_API_KEY` — OpenAI API key (required if USE_MOCK_CREW=false)
- `API_KEY` — Simple API key for MVP authentication
- `CORS_ORIGINS` — Comma-separated list of allowed origins

### Custom Configuration
```bash
# Copy and customize
cp .env.docker .env

# Edit as needed
nano .env

# Reload services
docker-compose down
docker-compose up -d
```

## Next Steps

See `project-context/3.deliver/deployment-plan.md` for:
- Detailed deployment procedures
- Rollback procedures
- Production readiness checklist
- Known limitations and future work
