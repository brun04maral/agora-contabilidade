# CI/CD Status - Agora Contabilidade

Este documento descreve o estado atual de CI/CD (Continuous Integration/Continuous Deployment) para o repositório Agora Contabilidade.

---

## 📊 Estado Atual: ❌ NÃO CONFIGURADO

### GitHub Actions
- **Status:** NÃO configurado
- **Localização:** Sem `.github/workflows/`
- **Deploy:** 100% manual via script `deploy.sh`

---

## 🔧 Método Atual: Deploy Manual

### Script deploy.sh
**Localização:** `/home/zumine/amp/docker/app/deploy.sh`

**Funcionalidades:**
1. ✅ **Backup automático** da database PostgreSQL
2. ✅ **Git pull** do branch atual
3. ✅ **Docker rebuild** (sem cache)
4. ✅ **Apply migrations** Django
5. ✅ **Collectstatic** (CSS, JS, assets)
6. ✅ **Health checks** (Django check, container status, HTTP)
7. ✅ **Limpeza** de backups antigos (30 dias)

**Uso:**
```bash
cd ~/amp/docker/app
./deploy.sh
```

**Output exemplo:**
```
🚀 Agora Deployment Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Step 1/7: Creating database backup...
✅ Backup created: backups/backup_20260105_143022.sql.gz

📥 Step 2/7: Pulling latest code...
✅ Code updated

🛑 Step 3/7: Stopping containers...
✅ Containers stopped

🏗️  Step 4/7: Building Docker images...
✅ Images built

🚀 Step 5/7: Starting services...
✅ Services started

🔄 Step 6/7: Running migrations...
✅ Migrations applied

📦 Collecting static files...
✅ Static files collected

🏥 Step 7/7: Running health checks...
✅ Django health check passed
✅ Container is running

🎉 Deployment Complete!

📍 Application: https://app.agoramediaproduction.pt
```

---

## 🎯 Workflow de Desenvolvimento

### Com VS Code Extension (Atual)

1. **Conectar VS Code** ao servidor via SSH
2. **Editar código** diretamente (Django models, views, templates)
3. **Testar localmente:**
   ```bash
   docker compose down
   docker compose up -d --build web
   docker compose logs -f web
   ```
4. **Testar no browser:**
   - https://app.agoramediaproduction.pt/admin

5. **Django shell testing:**
   ```bash
   docker compose exec web python manage.py shell
   >>> from core.models import Projeto, Socio
   >>> Socio.objects.all()
   ```

6. **Commit + Push:**
   ```bash
   git add agora_web/core/models.py
   git commit -m "feat: add receita mensal dashboard"
   git push
   ```

7. **Deploy final:**
   ```bash
   ./deploy.sh
   ```

---

### Com MCP GitHub (Remoto)

1. **Editar via MCP** (Perplexity, Claude.ai)
2. **Criar PR no GitHub**
3. **Merge para main**
4. **SSH manual para deploy:**
   ```bash
   ssh zumine@[servidor]
   cd ~/amp/docker/app
   ./deploy.sh
   ```

**Limitação:** Não há deploy automático.

---

## ⚠️ Peculiaridades Django

### Código na Imagem Docker
Diferente de montar volumes, o código Django está **dentro da imagem Docker**.

**Implicação:**
- Qualquer mudança em Python/templates **requer rebuild**:
  ```bash
  docker compose up -d --build web
  ```

### Migrations
Django migrations precisam ser aplicadas após mudanças em models:
```bash
# Criar migration (no VS Code/servidor)
docker compose exec web python manage.py makemigrations

# Aplicar migration
docker compose exec web python manage.py migrate

# Ou deixar o deploy.sh aplicar automaticamente
```

### Static Files
CSS, JS, imagens precisam de collectstatic:
```bash
docker compose exec web python manage.py collectstatic --noinput
```

**Nota:** `deploy.sh` faz isto automaticamente.

---

## ✅ Alternativas para CI/CD Automático

### Opção 1: Tailscale VPN + GitHub Actions (Recomendada)

**Como funciona:**
- Mesmo sistema que RAIA pode usar
- GitHub Actions conecta via Tailscale VPN
- Deploy automático em push para `main`

**Setup:**
1. **Instalar Tailscale** no servidor (se ainda não está)
2. **Criar `.github/workflows/deploy.yml`:**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Setup Tailscale
        uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TAILSCALE_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TAILSCALE_OAUTH_SECRET }}
          tags: tag:ci

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.TAILSCALE_SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/amp/docker/app
            ./deploy.sh
```

3. **GitHub Secrets:**
   - `TAILSCALE_OAUTH_CLIENT_ID`
   - `TAILSCALE_OAUTH_SECRET`
   - `TAILSCALE_SERVER_IP`
   - `SERVER_USER` (zumine)
   - `SSH_PRIVATE_KEY`

**Vantagens:**
- ✅ Deploy automático
- ✅ Sem exposição do servidor
- ✅ Usa o `deploy.sh` existente (backups, health checks)

---

### Opção 2: Self-Hosted Runner

**Como funciona:**
- Runner instalado no servidor
- Executa jobs localmente

**Desvantagens:**
- ❌ Requer manutenção
- ❌ Consome recursos
- ❌ Pode ficar offline

**Não recomendado** para este projeto.

---

### Opção 3: Manter Deploy Manual (Atual)

**Vantagens:**
- ✅ Funciona perfeitamente agora
- ✅ Controle total sobre deployment
- ✅ Testing antes de deploy
- ✅ Script `deploy.sh` é robusto

**Desvantagens:**
- ⚠️ Precisa SSH manual
- ⚠️ Não automatizado via MCP GitHub workflow

---

## 🎯 Recomendação

### Para Agora (2026 Q1): ✅ **Manter Deploy Manual**
- Script `deploy.sh` funciona perfeitamente
- Workflow VS Code Extension é eficiente
- Não há necessidade imediata de automação

### Para Futuro (2026 Q2+): ⭐ **Considerar Tailscale + GitHub Actions**
- Se começares a fazer muitos deploys via MCP GitHub
- Se quiseres CI/CD completo com testes automatizados
- Setup: ~30 min

---

## 📊 Comparação: RAIA vs Agora Contabilidade

| Feature | RAIA | Agora Contabilidade |
|---------|------|---------------------|
| **GitHub Actions** | Configurado (desativado) | Não configurado |
| **Deploy Script** | ✅ `deploy.sh` | ✅ `deploy.sh` |
| **Backup Automático** | ✅ SQLite | ✅ PostgreSQL |
| **Health Checks** | ✅ HTTP + DB | ✅ Django check + HTTP + DB |
| **Migrations** | ✅ SQL scripts | ✅ Django migrations |
| **Static Files** | N/A (SvelteKit build) | ✅ Collectstatic |
| **Servidor** | 192.168.1.69 | Mesmo servidor |
| **Deploy Atual** | Manual | Manual |

**Conclusão:** Ambos funcionam perfeitamente com deploy manual via script robusto.

---

## 🔮 Possível Evolução Futura

### Fase 1: Adicionar Testes (Sem CI/CD)
```bash
# No servidor, criar testes
docker compose exec web python manage.py test

# Adicionar ao workflow manual
# (rodar antes de deploy)
```

### Fase 2: Ativar Tailscale + GitHub Actions
- Deploy automático em push para `main`
- Rodar testes antes de deploy
- Notificações em caso de falha

### Fase 3: Staging Environment
- Branch `develop` → staging
- Branch `main` → production
- Testing em staging antes de production

---

## 📚 Documentação Relacionada

- **Workflows de IA:** [`.claude/workflows/README.md`](workflows/README.md)
- **VS Code Extension:** [`.claude/workflows/vscode-extension.md`](workflows/vscode-extension.md)
- **MCP GitHub:** [`.claude/workflows/mcp-github.md`](workflows/mcp-github.md)
- **Script de Deploy:** [`deploy.sh`](../deploy.sh)
- **Guia de Dev:** [`README-DEV.md`](../README-DEV.md)

---

## 🔧 Troubleshooting

### Deploy falha por falta de migrations
```bash
# Criar migration manualmente
docker compose exec web python manage.py makemigrations

# Deploy novamente
./deploy.sh
```

### CSS não atualiza
```bash
# Collectstatic manual
docker compose exec web python manage.py collectstatic --noinput --clear

# Ou rebuild completo
docker compose up -d --build web
```

### Health check falha
```bash
# Ver logs
docker compose logs -f web

# Django check
docker compose exec web python manage.py check --deploy
```

---

**Última Atualização:** 2026-01-05
**Status:** ❌ GitHub Actions não configurado, deploy manual via `./deploy.sh`
**Recomendação:** Manter deploy manual para desenvolvimento atual, considerar Tailscale CI/CD no futuro
