#!/bin/bash
#
# Script de Backup Automático - Agora Contabilidade PostgreSQL
#
# Este script faz backup da base de dados PostgreSQL e mantém os últimos 30 dias
#
# Uso:
#   ./backup.sh                    # Backup manual
#   Ou via cron: 0 3 * * * /path/to/backup.sh
#

set -e  # Exit on error

# Configuração
BACKUP_DIR="$HOME/backups/agora_contabilidade"
DOCKER_COMPOSE_PATH="$HOME/zumine/amp/docker/app/agora_web"
COMPOSE_FILE="docker-compose.cloudflare.yml"
RETENTION_DAYS=30

# Criar diretório de backups se não existir
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_ONLY=$(date +"%Y%m%d")
BACKUP_FILE="$BACKUP_DIR/agora_db_${TIMESTAMP}.sql.gz"
LATEST_LINK="$BACKUP_DIR/agora_db_latest.sql.gz"

echo "=================================="
echo "🔄 Backup Agora Contabilidade"
echo "=================================="
echo "Data: $(date)"
echo "Destino: $BACKUP_FILE"
echo ""

# Navegar para o diretório do docker-compose
cd "$DOCKER_COMPOSE_PATH"

# Fazer backup da base de dados PostgreSQL
echo "📦 A fazer backup da base de dados..."
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U agora agora_production | gzip > "$BACKUP_FILE"

# Verificar se o backup foi criado com sucesso
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup criado com sucesso: $SIZE"

    # Criar link simbólico para o último backup
    ln -sf "$BACKUP_FILE" "$LATEST_LINK"
    echo "🔗 Link 'latest' atualizado"
else
    echo "❌ Erro: Backup não foi criado!"
    exit 1
fi

# Limpar backups antigos (manter últimos 30 dias)
echo ""
echo "🧹 A limpar backups antigos (>${RETENTION_DAYS} dias)..."
find "$BACKUP_DIR" -name "agora_db_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "agora_db_*.sql.gz" -type f | wc -l)
echo "📊 Total de backups retidos: $TOTAL_BACKUPS"

echo ""
echo "=================================="
echo "✅ Backup concluído com sucesso!"
echo "=================================="
