#!/bin/bash
# Quick Deploy para Servidor Remoto
# Corre isto NO SERVIDOR Ubuntu via SSH!

set -e

echo "🚀 Agora Contabilidade - Quick Deploy"
echo "======================================"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# PASSO 1: Vai para o diretório de deploy ou clona
if [ -d ~/zumine/amp/docker/app/.git ]; then
    echo -e "${YELLOW}📥 Git pull...${NC}"
    cd ~/zumine/amp/docker/app
    git pull origin claude/self-hosted-brainstorm-heo8m
else
    echo -e "${YELLOW}📥 Git clone (primeira vez)...${NC}"
    mkdir -p ~/zumine/amp/docker
    cd ~/zumine/amp/docker

    # Remove app/ se existir mas não for git repo
    if [ -d app ] && [ ! -d app/.git ]; then
        echo "Removendo pasta app/ antiga (não é git repo)..."
        rm -rf app
    fi

    git clone https://github.com/brun04maral/agora-contabilidade.git app
    cd app
    git checkout claude/self-hosted-brainstorm-heo8m
fi

# PASSO 2: Vai para agora_web
cd ~/zumine/amp/docker/app/agora_web

# PASSO 3: Cria .env se não existir
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Criando .env...${NC}"
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=f#&l*&fzdxbrdttr1rjfn279x-aey=86p%a0a3yxgjj4-@vp12
DJANGO_SETTINGS_MODULE=config.settings
DOMAIN=app.agoramediaproduction.pt
ALLOWED_HOSTS=app.agoramediaproduction.pt,localhost,127.0.0.1
DB_NAME=agora_production
DB_USER=agora
DB_PASSWORD=Agora2025Prod!SecureDB
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
EOF
    echo -e "${GREEN}✅ .env criado!${NC}"
else
    echo -e "${GREEN}✅ .env já existe${NC}"
fi

# PASSO 4: Verifica Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não encontrado. A instalar...${NC}"
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${YELLOW}⚠️  Docker instalado! Faz LOGOUT e LOGIN de novo, depois corre este script outra vez.${NC}"
    exit 1
fi

# PASSO 5: Verifica network Traefik
if ! docker network ls | grep -q traefik_proxy; then
    echo -e "${YELLOW}🌐 Criando network traefik_proxy...${NC}"
    docker network create traefik_proxy
fi

# PASSO 6: Deploy!
echo -e "${YELLOW}🚀 A fazer deploy...${NC}"
chmod +x deploy.sh
./deploy.sh

echo ""
echo -e "${GREEN}✅ DEPLOY COMPLETO!${NC}"
echo ""
echo "🌐 Acede a: https://app.agoramediaproduction.pt"
echo "🔧 Admin: https://app.agoramediaproduction.pt/admin/"
echo ""
echo "Ver logs: cd ~/zumine/amp/docker/app/agora_web && docker-compose -f docker-compose.production.yml logs -f web"
