#!/bin/bash
# Deploy to Development/Test Server
# Usage: ./deploy_dev.sh

set -e  # Exit on error

echo "🚀 Deploying to Development Server..."
echo "Server: 202.92.140.157 (172.20.3.92)"
echo "Branch: staging"
echo ""

# Configuration
DEV_SERVER="172.20.3.92"
SSH_PORT="9913"
SSH_USER="ajbasa"
REMOTE_DIR="~/spmo_suite"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Pulling latest changes from staging branch...${NC}"
ssh -p $SSH_PORT $SSH_USER@$DEV_SERVER << 'ENDSSH'
cd ~/spmo_suite
git fetch origin
git checkout staging
git pull origin staging
ENDSSH

echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Restarting Docker containers...${NC}"
ssh -p $SSH_PORT $SSH_USER@$DEV_SERVER << 'ENDSSH'
cd ~/spmo_suite
docker-compose down
docker-compose up -d --build
ENDSSH

echo -e "${GREEN}✓ Containers restarted${NC}"
echo ""

echo -e "${YELLOW}Step 3: Running database migrations...${NC}"
ssh -p $SSH_PORT $SSH_USER@$DEV_SERVER << 'ENDSSH'
cd ~/spmo_suite
docker-compose exec -T app_hub python manage.py migrate
docker-compose exec -T app_gamit python manage.py migrate
docker-compose exec -T app_gfa python manage.py migrate
docker-compose exec -T app_store python manage.py migrate
ENDSSH

echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

echo -e "${YELLOW}Step 4: Collecting static files...${NC}"
ssh -p $SSH_PORT $SSH_USER@$DEV_SERVER << 'ENDSSH'
cd ~/spmo_suite
docker-compose exec -T app_hub python manage.py collectstatic --noinput
ENDSSH

echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 5: Checking container status...${NC}"
ssh -p $SSH_PORT $SSH_USER@$DEV_SERVER << 'ENDSSH'
cd ~/spmo_suite
docker-compose ps
ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Test the applications at:"
echo "  - https://sspmo-dev.up.edu.ph"
echo "  - https://gamit-sspmo-dev.up.edu.ph"
echo "  - https://lipad-sspmo-dev.up.edu.ph"
echo "  - https://suplay-sspmo-dev.up.edu.ph"
echo ""
