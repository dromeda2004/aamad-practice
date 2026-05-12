#!/bin/bash
# TalentFlow AI rollback script
# Usage: ./rollback.sh [previous-version]

set -e

VERSION=${1:-previous}
REGISTRY=${REGISTRY:-docker.io/talentflow}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== TalentFlow AI Rollback ===${NC}"
echo "Rolling back to version: $VERSION"
echo ""

# Step 1: Stop current services
echo -e "${YELLOW}Step 1: Stopping current services...${NC}"
docker-compose down

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to stop services${NC}"
    exit 1
fi

# Step 2: Pull previous version images
echo -e "${YELLOW}Step 2: Pulling previous version images...${NC}"
docker pull "$REGISTRY/backend:$VERSION"
docker pull "$REGISTRY/frontend:$VERSION"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to pull images${NC}"
    exit 1
fi

# Step 3: Start previous version
echo -e "${YELLOW}Step 3: Starting services with version $VERSION...${NC}"
docker-compose -e BACKEND_IMAGE="$REGISTRY/backend:$VERSION" \
               -e FRONTEND_IMAGE="$REGISTRY/frontend:$VERSION" up -d

sleep 5

# Step 4: Health check
echo -e "${YELLOW}Step 4: Verifying rollback...${NC}"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Rollback successful${NC}"
    echo -e "${GREEN}Services are running with version $VERSION${NC}"
else
    echo -e "${RED}✗ Rollback verification failed${NC}"
    echo "Run 'docker-compose logs' for details"
    exit 1
fi

# Step 5: Summary
echo -e "\n${GREEN}=== Rollback Complete ===${NC}"
echo "Current version: $VERSION"
echo ""
echo "Recommended next steps:"
echo "  1. Monitor logs: docker-compose logs -f"
echo "  2. Verify functionality: curl http://localhost:8000/api/v1/health"
echo "  3. Investigate failed version: git log, docker logs, etc."
echo ""
