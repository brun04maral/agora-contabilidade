#!/bin/bash
#
# 🚀 Agora Deployment Script
# Automated deployment with backup, build, migrations, and health checks
#
# Usage: ./deploy.sh
# Server location: /home/zumine/amp/docker/app/
#

set -e  # Exit on any error

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_RETENTION_DAYS=30

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 Agora Deployment Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# 1. Database Backup
echo -e "${YELLOW}📦 Step 1/7: Creating database backup...${NC}"
if docker compose ps db | grep -q "Up"; then
    BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"
    docker compose exec -T db pg_dump -U agora agora_production > "$BACKUP_FILE"

    # Compress the backup
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup created: ${BACKUP_FILE}.gz${NC}"

    # Clean old backups
    echo "🧹 Cleaning backups older than ${BACKUP_RETENTION_DAYS} days..."
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete
else
    echo -e "${YELLOW}⚠️  Database not running, skipping backup${NC}"
fi

# 2. Pull latest code
echo ""
echo -e "${YELLOW}📥 Step 2/7: Pulling latest code...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: ${CURRENT_BRANCH}"
git pull origin "${CURRENT_BRANCH}"
echo -e "${GREEN}✅ Code updated${NC}"

# 3. Stop containers
echo ""
echo -e "${YELLOW}🛑 Step 3/7: Stopping containers...${NC}"
docker compose down
echo -e "${GREEN}✅ Containers stopped${NC}"

# 4. Build new images
echo ""
echo -e "${YELLOW}🏗️  Step 4/7: Building Docker images...${NC}"
docker compose build --no-cache web
echo -e "${GREEN}✅ Images built${NC}"

# 5. Start services
echo ""
echo -e "${YELLOW}🚀 Step 5/7: Starting services...${NC}"
docker compose up -d
echo -e "${GREEN}✅ Services started${NC}"

# Wait for database to be ready
echo ""
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# 6. Run migrations and collect static
echo ""
echo -e "${YELLOW}🔄 Step 6/7: Running migrations...${NC}"
docker compose exec web python manage.py migrate
echo -e "${GREEN}✅ Migrations applied${NC}"

echo ""
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker compose exec web python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Static files collected${NC}"

# 7. Health checks
echo ""
echo -e "${YELLOW}🏥 Step 7/7: Running health checks...${NC}"

# Django check
if docker compose exec web python manage.py check --deploy 2>&1 | grep -q "System check identified no issues"; then
    echo -e "${GREEN}✅ Django health check passed${NC}"
else
    echo -e "${RED}⚠️  Django health check warnings (check logs)${NC}"
fi

# Container status
echo ""
echo "Container status:"
docker compose ps

# Final summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Application: https://app.agoramediaproduction.pt"
echo "🔧 Admin: https://app.agoramediaproduction.pt/admin/"
echo "📊 Logs: docker compose logs -f web"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
