===============================================================================
MANUTENÇÃO E OPERAÇÕES: Backup, Updates e Troubleshooting
Guia completo para manter o sistema em produção
===============================================================================

==================================================
VISÃO GERAL
==================================================

OBJECTIVO: Garantir funcionamento estável e seguro do sistema em produção

TÓPICOS:
✓ Backups automáticos
✓ Actualizações de dependências
✓ Monitorização
✓ Troubleshooting comum
✓ Procedimentos de emergência

FREQUÊNCIA RECOMENDADA:
- Backups: Diário (automático)
- Health checks: Semanal
- Updates: Mensal
- Review logs: Semanal

==================================================
1. ESTRATÉGIA DE BACKUP
==================================================

1.1 BACKUP AUTOMÁTICO DIÁRIO
--------------------

Ficheiro: `scripts/backup-db.sh`

```bash
#!/bin/bash

# Backup automático PostgreSQL
# Executar via cron diariamente

set -e

# Configuração
DB_NAME="agora_contabilidade"
DB_USER="agora_user"
BACKUP_DIR="/var/backups/agora-contabilidade"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sql.gz"
KEEP_DAYS=30

# Criar directório se não existir
mkdir -p ${BACKUP_DIR}

# Backup PostgreSQL
echo "[$(date)] Iniciando backup..."
pg_dump -U ${DB_USER} -h localhost ${DB_NAME} | gzip > ${BACKUP_FILE}

# Verificar sucesso
if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ Backup criado: ${BACKUP_FILE}"
    
    # Verificar tamanho
    SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
    echo "[$(date)] Tamanho: ${SIZE}"
else
    echo "[$(date)] ❌ Erro ao criar backup!"
    exit 1
fi

# Limpar backups antigos (manter últimos 30 dias)
echo "[$(date)] Limpando backups antigos..."
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +${KEEP_DAYS} -delete
echo "[$(date)] ✅ Limpeza completa"

# Opcional: Upload para cloud
# aws s3 cp ${BACKUP_FILE} s3://agora-backups/
# rclone copy ${BACKUP_FILE} gdrive:agora-backups/

echo "[$(date)] 🎉 Backup completo!"
```

Dar permissões:
```bash
chmod +x scripts/backup-db.sh
```

Configurar cron (executar 3h da manhã):
```bash
crontab -e

# Adicionar linha:
0 3 * * * /path/to/agora-contabilidade/scripts/backup-db.sh >> /var/log/agora-backup.log 2>&1
```

1.2 BACKUP FICHEIROS UPLOAD
--------------------

Ficheiro: `scripts/backup-uploads.sh`

```bash
#!/bin/bash

# Backup de ficheiros uploaded (PDFs, imagens)

set -e

UPLOAD_DIR="./data/uploads"
BACKUP_DIR="/var/backups/agora-contabilidade/uploads"
DATE=$(date +%Y%m%d)

mkdir -p ${BACKUP_DIR}

# Criar arquivo tar.gz
tar -czf ${BACKUP_DIR}/uploads_${DATE}.tar.gz ${UPLOAD_DIR}

echo "✅ Backup uploads criado: uploads_${DATE}.tar.gz"

# Limpar backups > 60 dias
find ${BACKUP_DIR} -name "uploads_*.tar.gz" -mtime +60 -delete
```

1.3 RESTAURAR BACKUP
--------------------

Processo manual:

PASSO 1: Parar aplicação
```bash
docker-compose down
# OU
systemctl stop agora-contabilidade
```

PASSO 2: Restaurar database
```bash
# Listar backups disponíveis
ls -lh /var/backups/agora-contabilidade/

# Escolher backup (ex: backup_20251218_030000.sql.gz)
BACKUP_FILE="/var/backups/agora-contabilidade/backup_20251218_030000.sql.gz"

# Limpar database actual
psql -U agora_user -h localhost -c "DROP DATABASE IF EXISTS agora_contabilidade;"
psql -U agora_user -h localhost -c "CREATE DATABASE agora_contabilidade;"

# Restaurar
gunzip -c ${BACKUP_FILE} | psql -U agora_user -h localhost agora_contabilidade

echo "✅ Database restaurada"
```

PASSO 3: Restaurar uploads (se necessário)
```bash
UPLOAD_BACKUP="/var/backups/agora-contabilidade/uploads/uploads_20251218.tar.gz"

# Limpar uploads actuais
rm -rf ./data/uploads/*

# Extrair backup
tar -xzf ${UPLOAD_BACKUP} -C ./
```

PASSO 4: Reiniciar aplicação
```bash
docker-compose up -d
# OU
systemctl start agora-contabilidade
```

PASSO 5: Verificar
```bash
# Testar login
curl http://localhost:7331

# Verificar logs
docker-compose logs -f app
```

1.4 BACKUP PARA CLOUD
--------------------

Opção A: AWS S3
```bash
# Instalar AWS CLI
sudo apt install awscli

# Configurar credenciais
aws configure

# Script backup para S3
#!/bin/bash
BACKUP_FILE="/var/backups/agora-contabilidade/backup_$(date +%Y%m%d).sql.gz"
S3_BUCKET="s3://agora-backups"

# Upload
aws s3 cp ${BACKUP_FILE} ${S3_BUCKET}/database/
aws s3 cp /var/backups/agora-contabilidade/uploads/ ${S3_BUCKET}/uploads/ --recursive

echo "✅ Backup enviado para S3"
```

Opção B: Google Drive (rclone)
```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar
rclone config

# Script
rclone copy /var/backups/agora-contabilidade gdrive:agora-backups/
```

Opção C: Rsync para servidor remoto
```bash
#!/bin/bash
REMOTE_USER="backup"
REMOTE_HOST="backup.example.com"
REMOTE_PATH="/backups/agora/"

rsync -avz --delete \
  /var/backups/agora-contabilidade/ \
  ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}
```

==================================================
2. ACTUALIZAÇÕES DE SISTEMA
==================================================

2.1 ACTUALIZAR DEPENDÊNCIAS NPM
--------------------

Procedimento mensal:

```bash
# Ver dependências desactualizadas
npm outdated

# Actualizar minor/patch versions (seguro)
npm update

# Testar
npm run build
npm run dev

# Correr em produção se tudo OK
git add package*.json
git commit -m "chore: update dependencies"
git push
```

CRÍTICO: Testar sempre em dev antes de produção!

Dependências críticas a monitorizar:
- next (framework)
- prisma (database)
- @prisma/client
- react, react-dom

2.2 ACTUALIZAR PRISMA
--------------------

Quando nova versão Prisma sai:

```bash
# Ver versão actual
npx prisma --version

# Actualizar Prisma CLI e Client
npm install prisma@latest @prisma/client@latest

# Regenerar client
npx prisma generate

# Verificar migrations
npx prisma migrate status

# Testar
npm run build
```

2.3 ACTUALIZAR NEXT.JS
--------------------

Cuidado: Major versions podem ter breaking changes!

```bash
# Ver versão actual
npm list next

# Ler changelog
# https://github.com/vercel/next.js/releases

# Actualizar (minor version)
npm install next@latest

# Verificar breaking changes
npm run build

# Testar todas as rotas
npm run dev
```

2.4 ACTUALIZAR DOCKER IMAGES
--------------------

Se usar Docker em produção:

```bash
# Rebuild image
docker-compose build --no-cache

# Parar containers actuais
docker-compose down

# Iniciar com nova image
docker-compose up -d

# Verificar logs
docker-compose logs -f app

# Verificar saúde
curl http://localhost:7331/api/health
```

==================================================
3. MONITORIZAÇÃO
==================================================

3.1 HEALTH CHECK ENDPOINT
--------------------

Ficheiro: `app/api/health/route.ts`

```typescript
import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

export async function GET() {
  try {
    // Testar conexão database
    await prisma.$queryRaw`SELECT 1`
    
    // Verificar disk space (se aplicável)
    // const diskUsage = await checkDiskUsage()
    
    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
      uptime: process.uptime()
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: String(error)
      },
      { status: 503 }
    )
  }
}
```

Monitorizar via cron:
```bash
#!/bin/bash
# scripts/health-check.sh

HEALTH_URL="http://localhost:7331/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${HEALTH_URL})

if [ ${RESPONSE} -eq 200 ]; then
    echo "[$(date)] ✅ Sistema saudável"
else
    echo "[$(date)] ❌ Sistema com problemas! HTTP ${RESPONSE}"
    
    # Enviar alerta (exemplo)
    # curl -X POST https://hooks.slack.com/services/... \
    #   -d '{"text":"⚠️ Agora Contabilidade DOWN!"}'
    
    # Ou email
    # echo "Sistema DOWN" | mail -s "Alerta Agora" admin@agoramedia.pt
fi
```

Cron (executar de 15 em 15 minutos):
```bash
*/15 * * * * /path/to/scripts/health-check.sh >> /var/log/agora-health.log 2>&1
```

3.2 LOGS
--------------------

Ver logs aplicação:

Docker:
```bash
# Últimas 100 linhas
docker-compose logs --tail=100 app

# Follow (tempo real)
docker-compose logs -f app

# Procurar erros
docker-compose logs app | grep ERROR
```

Systemd:
```bash
journalctl -u agora-contabilidade -n 100
journalctl -u agora-contabilidade -f
```

Log PostgreSQL:
```bash
# Localização comum
tail -f /var/log/postgresql/postgresql-16-main.log

# Via Docker
docker-compose logs db
```

3.3 MÉTRICAS IMPORTANTES
--------------------

Verificar semanalmente:

□ Espaço em disco
```bash
df -h
# /var deve ter > 20% livre
```

□ Uso memória
```bash
free -h
# Swap não deve estar cheio
```

□ Tamanho database
```bash
psql -U agora_user -h localhost agora_contabilidade -c "\l+"
```

□ Número de transactions
```bash
psql -U agora_user -h localhost agora_contabilidade \
  -c "SELECT COUNT(*) FROM transactions;"
```

□ Erros recentes
```bash
docker-compose logs app --since 24h | grep -i error | wc -l
# Deve ser 0 ou muito baixo
```

==================================================
4. TROUBLESHOOTING COMUM
==================================================

4.1 APLICAÇÃO NÃO INICIA
--------------------

SINTOMA: docker-compose up falha ou app crasha

DIAGNÓSTICO:
```bash
# Ver logs
docker-compose logs app

# Verificar portas
netstat -tulpn | grep 7331
# Porta já em uso?

# Verificar .env
cat .env | grep DATABASE_URL
# Credenciais correctas?
```

SOLUÇÕES:

Problema: Porta 7331 em uso
```bash
# Matar processo
lsof -ti:7331 | xargs kill -9

# Ou mudar porta no .env
PORT=7332
```

Problema: Database não conecta
```bash
# Testar conexão manual
psql postgresql://user:pass@localhost:5432/agora_contabilidade

# Verificar PostgreSQL está a correr
systemctl status postgresql

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

Problema: Prisma Client desactualizado
```bash
npx prisma generate
npm run build
```

4.2 QUERIES LENTAS
--------------------

SINTOMA: Dashboard demora > 3 segundos a carregar

DIAGNÓSTICO:
```bash
# Enable query logging
# Adicionar ao .env:
DEBUG=prisma:query

# Restartar app
docker-compose restart app

# Ver queries
docker-compose logs app | grep "prisma:query"
```

SOLUÇÕES:

Adicionar indexes:
```prisma
# Editar schema.prisma
model Transaction {
  // ...
  @@index([userId, type, categoryCode])
  @@index([userId, projectCode])
  @@index([issuedAt])
}
```

```bash
# Criar migration
npx prisma migrate dev --name add_performance_indexes

# Deploy
npx prisma migrate deploy
```

Optimizar queries:
```typescript
// Antes (N+1 queries)
const transactions = await prisma.transaction.findMany()
for (const t of transactions) {
  const user = await prisma.user.findUnique({ where: { id: t.userId } })
}

// Depois (1 query)
const transactions = await prisma.transaction.findMany({
  include: { user: true }
})
```

4.3 ERROS DE CÁLCULO (SALDOS ERRADOS)
--------------------

SINTOMA: Saldos na UI não batem com expectativa

DIAGNÓSTICO:
```bash
# Abrir Prisma Studio
npx prisma studio

# Verificar transactions manualmente
# Filtrar por:
# - userId
# - type (income/expense)
# - categoryCode
# - projectCode

# Executar query SQL directa
psql -U agora_user agora_contabilidade
```

```sql
SELECT 
  type,
  "categoryCode",
  "projectCode",
  COUNT(*),
  SUM(total) / 100 as total_euros
FROM transactions
WHERE "userId" = 'bruno-uuid'
GROUP BY type, "categoryCode", "projectCode";
```

SOLUÇÕES COMUNS:

Problema: Despesas não estão negativas
```sql
# Verificar em Prisma Studio
# Transactions type='expense' devem ter total < 0

# Corrigir se necessário
UPDATE transactions 
SET total = -ABS(total)
WHERE type = 'expense' AND total > 0;
```

Problema: Estado pagamento inconsistente
```sql
# Verificar extra JSON
SELECT id, extra->>'estado_pagamento' 
FROM transactions 
WHERE type = 'expense';

# Deve ser 'PAGO' ou 'PENDENTE'
```

Problema: Conversão cêntimos errada
```sql
# Transactions devem estar em cêntimos (x100)
# 150.00 EUR = 15000 cêntimos

# Se valores estão errados, corrigir:
UPDATE transactions SET total = total * 100 WHERE ...;
```

4.4 FICHEIROS UPLOAD NÃO APARECEM
--------------------

SINTOMA: PDFs uploaded não aparecem na UI

DIAGNÓSTICO:
```bash
# Verificar directório existe
ls -la ./data/uploads

# Verificar permissões
# Directório deve ser writable pelo user da app

# Verificar .env
echo $UPLOAD_PATH
# Deve apontar para directório correcto
```

SOLUÇÕES:

Corrigir permissões:
```bash
# Dar ownership ao user correcto
sudo chown -R www-data:www-data ./data/uploads

# Ou se Docker
sudo chown -R 1000:1000 ./data/uploads

# Permissões 755
chmod 755 ./data/uploads
```

Criar directório:
```bash
mkdir -p ./data/uploads
chmod 755 ./data/uploads
```

4.5 ERROS TOCONLINE API
--------------------

SINTOMA: Emissão de facturas falha

DIAGNÓSTICO:
```bash
# Verificar API key
psql agora_contabilidade -c \
  "SELECT value FROM settings WHERE code = 'TOCONLINE_API_KEY';"

# Testar conexão manualmente
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.toconline.pt/v1/customers
```

SOLUÇÕES:

Problema: API key inválida
```sql
# Gerar nova key em toconline.pt
# Actualizar no sistema:

# Via UI: /toconline
# Ou via SQL:
UPDATE settings 
SET value = 'nova_api_key' 
WHERE code = 'TOCONLINE_API_KEY';
```

Problema: Cliente não existe
```
# Criar cliente primeiro
# Verificar NIF está correcto
# Email é obrigatório
```

Problema: Rate limit
```typescript
# TOConline pode ter limites de requests
# Implementar retry com backoff

async function emitirComRetry(transactionId, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await emitirFactura(transactionId)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(r => setTimeout(r, 2000 * (i + 1)))
    }
  }
}
```

==================================================
5. PROCEDIMENTOS DE EMERGÊNCIA
==================================================

5.1 SISTEMA DOWN - RECOVERY RÁPIDO
--------------------

PASSOS:

1. Verificar o que está down
```bash
# App?
curl http://localhost:7331

# Database?
psql -U agora_user -h localhost agora_contabilidade -c "SELECT 1"
```

2. Reiniciar serviços
```bash
# Docker
docker-compose restart

# Systemd
sudo systemctl restart agora-contabilidade
sudo systemctl restart postgresql
```

3. Se persistir, restaurar último backup
```bash
# Ver backup mais recente
ls -lt /var/backups/agora-contabilidade/ | head -n 5

# Restaurar (ver secção 1.3)
```

4. Notificar utilizadores
```
# Se vai demorar > 15 min
# Email/SMS para Bruno e Rafael
```

5.2 CORRUPÇÃO DE DADOS
--------------------

SINTOMA: Dados inconsistentes, valores estranhos

PASSOS:

1. Parar sistema IMEDIATAMENTE
```bash
docker-compose down
```

2. Fazer backup do estado actual
```bash
pg_dump agora_contabilidade > corrupted_backup_$(date +%Y%m%d_%H%M%S).sql
```

3. Analisar o problema
```bash
# Usar Prisma Studio
npx prisma studio

# Queries SQL para investigar
```

4. Restaurar último backup bom
```bash
# Identificar último backup antes da corrupção
# Restaurar (ver 1.3)
```

5. Re-inserir dados críticos manualmente se necessário

5.3 PERDA DE DADOS
--------------------

Se backup falhou e perderam-se dados:

1. NÃO ENTRAR EM PÂNICO
2. Parar sistema
3. Verificar backups disponíveis:
```bash
ls -lh /var/backups/agora-contabilidade/
ls -lh /var/backups/agora-contabilidade/uploads/
```

4. Se backups cloud, restaurar:
```bash
# S3
aws s3 cp s3://agora-backups/database/backup_YYYYMMDD.sql.gz ./

# Google Drive
rclone copy gdrive:agora-backups/ ./restore/
```

5. Restaurar backup mais recente possível

6. Avaliar lacuna de dados:
```
# Último backup: 18/12/2025 03:00
# Perda de dados: 18/12/2025 03:00 - 14:00 (11 horas)
```

7. Recuperar manualmente:
   - Consultar emails de notificações
   - Exportar dados de app Python (se ainda activa)
   - Consultar facturas TOConline
   - Reconstrucao manual

==================================================
6. SEGURANÇA
==================================================

6.1 CHECKLIST SEGURANÇA MENSAL
--------------------

□ Passwords actualizadas
```bash
# Mudar passwords users a cada 3 meses
# Usar passwords fortes (> 16 chars)
```

□ API keys rotacionadas
```
# TOConline API key
# Outras integrações
```

□ SSL/TLS válido
```bash
# Se usar HTTPS, verificar certificado não expirou
openssl s_client -connect localhost:443 -servername agoramedia.pt
```

□ Firewall configurado
```bash
# Apenas portas necessárias abertas
sudo ufw status

# PostgreSQL: apenas localhost
# App: apenas 7331 (se necessário)
```

□ Logs auditados
```bash
# Procurar tentativas login falhadas
grep "login failed" /var/log/agora-*.log

# Verificar acessos suspeitos
```

6.2 BACKUP ENCRYPTION
--------------------

Encriptar backups sensíveis:

```bash
#!/bin/bash
# Backup encriptado com GPG

BACKUP_FILE="backup_$(date +%Y%m%d).sql.gz"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Criar backup
pg_dump agora_contabilidade | gzip > ${BACKUP_FILE}

# Encriptar
gpg --symmetric --cipher-algo AES256 ${BACKUP_FILE}

# Remover original não encriptado
rm ${BACKUP_FILE}

echo "✅ Backup encriptado: ${ENCRYPTED_FILE}"

# Upload encriptado
aws s3 cp ${ENCRYPTED_FILE} s3://agora-backups/encrypted/
```

Desencriptar:
```bash
gpg --decrypt backup_20251218.sql.gz.gpg | gunzip | psql agora_contabilidade
```

==================================================
7. DOCUMENTAÇÃO PARA EQUIPA
==================================================

7.1 RUNBOOK OPERAÇÕES
--------------------

Criar ficheiro: RUNBOOK.md

Conteúdo:
```markdown
# RUNBOOK - Operações Diárias

## Contactos de Emergência
- Bruno: +351 XXX XXX XXX
- Rafael: +351 YYY YYY YYY
- Hosting: support@hosting.com

## URLs Importantes
- App Produção: https://contabilidade.agoramedia.pt
- Prisma Studio: http://localhost:5555
- Backups: /var/backups/agora-contabilidade/

## Comandos Rápidos

Reiniciar sistema:
  docker-compose restart

Ver logs:
  docker-compose logs -f app

Backup manual:
  ./scripts/backup-db.sh

Restaurar backup:
  [seguir guia em MANUTENCAO.md secção 1.3]

## Procedimentos Semanais
Segunda: Verificar logs da semana
Sexta: Verificar espaço disco + backups

## Alertas
Se receber email/SMS alerta:
1. Verificar /api/health
2. Ver logs
3. Contactar equipa se necessário
```

7.2 CHANGE LOG
--------------------

Manter ficheiro: CHANGELOG.md

```markdown
# Changelog

## [1.2.0] - 2025-01-15
### Added
- Integração TOConline para emissão facturas
- Dashboard impostos com IVA trimestral

### Changed
- Optimizado queries saldos (20% mais rápido)

### Fixed
- Bug cálculo despesas fixas dividir por 2

## [1.1.0] - 2024-12-20
### Added
- Sistema orçamentos
- Catálogo equipamento

## [1.0.0] - 2024-12-01
### Initial Release
- Migração completa de app Python
- Cálculo saldos pessoais
- Dashboard fiscal
```

==================================================
CHECKLIST MANUTENÇÃO MENSAL
==================================================

DIA 1 DO MÊS:

□ Verificar backups últimos 30 dias
  - Todos os dias têm backup?
  - Tamanhos consistentes?
  - Testar restaurar último backup em ambiente dev

□ Actualizar dependências
  - npm outdated
  - Ler changelogs
  - Actualizar minor versions
  - Testar em dev
  - Deploy produção

□ Review logs
  - Procurar erros recentes
  - Identificar padrões
  - Optimizar queries lentas

□ Verificar métricas
  - Espaço disco
  - Uso CPU/memória
  - Tamanho database
  - Número transactions

□ Segurança
  - Verificar SSL válido
  - Auditar acessos
  - Rotacionar API keys (se necessário)

□ Testes manuais
  - Login funciona
  - Saldos calculam correctamente
  - Criar transaction
  - Exportar CSV
  - Emitir factura TOConline (se configurado)

□ Documentação
  - Actualizar CHANGELOG
  - Documentar mudanças
  - Actualizar RUNBOOK se necessário

==================================================
RECURSOS ÚTEIS
==================================================

LINKS:
- Prisma Docs: https://www.prisma.io/docs
- Next.js Docs: https://nextjs.org/docs
- PostgreSQL Manual: https://www.postgresql.org/docs/
- Docker Compose: https://docs.docker.com/compose/

COMANDOS ÚTEIS:

Prisma:
```bash
npx prisma studio
npx prisma migrate status
npx prisma db push
```

Docker:
```bash
docker-compose ps
docker-compose logs -f
docker-compose exec app sh
```

PostgreSQL:
```bash
psql -U user -d dbname
\dt         # listar tabelas
\d table    # descrever tabela
\q          # sair
```

Git:
```bash
git log --oneline -10
git diff
git status
```

==================================================
