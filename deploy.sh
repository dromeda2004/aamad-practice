#!/bin/bash
# TalentFlow AI deployment script
# Usage: ./deploy.sh [staging|production] [version]

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
REGISTRY=${REGISTRY:-docker.io/talentflow}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TalentFlow AI Deployment ===${NC}"
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be 'staging' or 'production'${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "Loading .env.$ENVIRONMENT"
    export $(cat .env.$ENVIRONMENT | xargs)
else
    echo -e "${YELLOW}Warning: .env.$ENVIRONMENT not found, using defaults${NC}"
fi

# Step 1: Build images
echo -e "\n${GREEN}Step 1: Building Docker images...${NC}"
docker build -f Dockerfile.backend -t "$REGISTRY/backend:$VERSION" .
docker build -f Dockerfile.frontend -t "$REGISTRY/frontend:$VERSION" .

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}Build successful${NC}"

# Step 2: Local validation (docker-compose up)
echo -e "\n${GREEN}Step 2: Running local validation...${NC}"
docker-compose -f docker-compose.yml up -d

sleep 5

# Step 3: Health checks
echo -e "\n${GREEN}Step 3: Running health checks...${NC}"

BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed (HTTP $BACKEND_HEALTH)${NC}"
    docker-compose logs backend
    exit 1
fi

FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Frontend health check passed${NC}"
else
    echo -e "${RED}✗ Frontend health check failed (HTTP $FRONTEND_HEALTH)${NC}"
    docker-compose logs frontend
    exit 1
fi

# Step 4: Smoke test
echo -e "\n${GREEN}Step 4: Running smoke test...${NC}"
SMOKE_TEST=$(curl -s -X POST http://localhost:8000/api/v1/runs \
    -H "Content-Type: application/json" \
    -d '{
        "requisition": {
            "role_title": "Test Engineer",
            "must_have_skills": ["Testing"],
            "preferred_skills": ["Automation"],
            "experience_min_years": 2,
            "experience_max_years": 5,
            "location": "Remote",
            "employment_type": "full-time",
            "free_text_brief": ""
        }
    }')

if echo "$SMOKE_TEST" | grep -q '"run_id"'; then
    echo -e "${GREEN}✓ Smoke test passed (run created)${NC}"
else
    echo -e "${RED}✗ Smoke test failed${NC}"
    echo "$SMOKE_TEST"
    exit 1
fi

# Step 5: Summary
echo -e "\n${GREEN}=== Deployment Summary ===${NC}"
echo "Frontend:  $REGISTRY/frontend:$VERSION"
echo "Backend:   $REGISTRY/backend:$VERSION"
echo ""
echo -e "${GREEN}Status: ✓ All checks passed${NC}"
echo ""
echo "Next steps for production deployment:"
echo "  1. Push images to registry: docker push $REGISTRY/backend:$VERSION"
echo "  2. Deploy on target host: ssh deploy@host && docker pull && docker-compose up -d"
echo "  3. Monitor: docker-compose logs -f"
echo ""
