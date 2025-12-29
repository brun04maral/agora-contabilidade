#!/bin/bash
# Deploy script for Agora Contabilidade Django app
# Run this script from: ~/zumine/amp/docker/app/agora_web/

set -e  # Exit on error

echo "🚀 Agora Contabilidade - Deploy Script"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: manage.py not found!${NC}"
    echo "Please run this script from the agora_web directory"
    echo "cd ~/zumine/amp/docker/app/agora_web && ./deploy.sh"
    exit 1
fi

echo -e "${GREEN}✅ Working directory: $(pwd)${NC}"

# Step 2: Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env not found!${NC}"
    echo "Please create .env with your configuration"
    echo "Template available in .env.production"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"

# Step 3: Stop existing containers (if any)
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down || true

# Step 4: Pull/Build images
echo -e "${YELLOW}🏗️  Building Docker images...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Step 5: Start database first
echo -e "${YELLOW}🗄️  Starting database...${NC}"
docker-compose -f docker-compose.production.yml up -d db

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Step 6: Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker-compose -f docker-compose.production.yml run --rm web python manage.py migrate --noinput

# Step 7: Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker-compose -f docker-compose.production.yml run --rm web python manage.py collectstatic --noinput

# Step 8: Create superuser (if needed)
echo -e "${YELLOW}👤 Creating superuser...${NC}"
echo "You can skip this if you already have a superuser"
docker-compose -f docker-compose.production.yml run --rm web python manage.py createsuperuser || true

# Step 9: Start all services
echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Step 10: Show status
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Container status:"
docker-compose -f docker-compose.production.yml ps
echo ""
echo "🌐 Application URL: https://app.agoramediaproduction.pt"
echo "🔧 Admin URL: https://app.agoramediaproduction.pt/admin/"
echo ""
echo "📝 View logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f web"
echo ""
echo "🔄 Restart services:"
echo "   docker-compose -f docker-compose.production.yml restart"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.production.yml down"
