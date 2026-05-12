#!/bin/bash
# TalentFlow AI health check script
# Usage: ./health-check.sh [backend-url] [frontend-url]

BACKEND_URL=${1:-http://localhost:8000}
FRONTEND_URL=${2:-http://localhost:3000}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TalentFlow AI Health Check ===${NC}"
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

FAILED=0

# Check backend health
echo -e "${YELLOW}Checking backend health...${NC}"
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health")

if [ "$BACKEND_STATUS" = "200" ]; then
    BACKEND_DATA=$(curl -s "$BACKEND_URL/api/v1/health")
    echo -e "${GREEN}✓ Backend is healthy (HTTP $BACKEND_STATUS)${NC}"
    echo "  Response: $BACKEND_DATA"
else
    echo -e "${RED}✗ Backend health check failed (HTTP $BACKEND_STATUS)${NC}"
    FAILED=1
fi

echo ""

# Check frontend health
echo -e "${YELLOW}Checking frontend health...${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is accessible (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}✗ Frontend health check failed (HTTP $FRONTEND_STATUS)${NC}"
    FAILED=1
fi

echo ""

# Smoke test: Create a run
echo -e "${YELLOW}Running smoke test (creating a run)...${NC}"
SMOKE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/runs" \
    -H "Content-Type: application/json" \
    -d '{
        "requisition": {
            "role_title": "Health Check Test",
            "must_have_skills": ["Testing"],
            "preferred_skills": ["Verification"],
            "experience_min_years": 1,
            "experience_max_years": 3,
            "location": "Remote",
            "employment_type": "full_time",
            "free_text_brief": ""
        }
    }')

if echo "$SMOKE_RESPONSE" | grep -q '"run_id"'; then
    RUN_ID=$(echo "$SMOKE_RESPONSE" | grep -o '"run_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Smoke test passed (run_id: $RUN_ID)${NC}"
else
    echo -e "${RED}✗ Smoke test failed${NC}"
    echo "Response: $SMOKE_RESPONSE"
    FAILED=1
fi

echo ""

# Summary
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}=== All Checks Passed ===${NC}"
    exit 0
else
    echo -e "${RED}=== Some Checks Failed ===${NC}"
    exit 1
fi
