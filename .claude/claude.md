# Agora Contabilidade - Claude Code Context

## 📋 Overview

Sistema de contabilidade Django para **Amaral & Reigota - Produção Audiovisual, Lda**
- **NIPC:** 518 351 190
- **Marca:** Agora Media Production
- **Sócios:** Bruno Amaral (BA) e Rafael Reigota (RR)

**Tech Stack:**
- Django 5.0 + PostgreSQL 16
- Unfold Admin Theme
- Docker + Traefik (reverse proxy)
- Cloudflare (DNS + Proxy + SSL)
- Python 3.11

**Deployment:** Production via Docker Compose com Traefik como reverse proxy local. Cloudflare fornece DNS, proxy e SSL (não Cloudflare Tunnel).

---

## ⚠️ CRÍTICO: Ambiente de Trabalho

**Workflow Atual:** VS Code Extension (Direto no Servidor)

### 🎯 Ambiente ÚNICO (Servidor de Produção)
- **Path:** `/home/zumine/amp/docker/app/`
- **Onde:** Servidor de produção
- **Acesso:** VS Code via SSH + Claude Extension
- **Vantagem:** Mudanças diretas, sem sincronização entre ambientes

### 🔄 Workflow Simplificado

**Com VS Code Extension:**
1. VS Code conecta ao servidor via SSH
2. Claude (extension) trabalha DIRETAMENTE no código do servidor
3. Testa localmente (rebuild Docker)
4. Commit + push quando pronto
5. Deploy final (já estamos no servidor!)

**Sem worktrees, sem pull entre ambientes!**

### ⚠️ Nota Histórica

Workflow antigo (DESCONTINUADO):
~~Claude standalone app → worktrees locais → push → pull no servidor~~

Documentação antiga arquivada em `archive-old-tkinter-app/`

---

## 🏗️ Arquitetura

```
~/amp/docker/app/
├── agora_web/              # 🎯 Django application (trabalha aqui!)
│   ├── core/               # Main app
│   │   ├── models.py       # Socio, Projeto, Despesa, Boletim, Saldo, etc.
│   │   ├── admin.py        # Unfold admin customizations
│   │   ├── utils/
│   │   │   └── saldos.py   # SaldosCalculator - lógica de cálculo
│   │   ├── templates/
│   │   │   └── admin/core/saldo/changelist.html
│   │   ├── fixtures/
│   │   │   └── socios.json # BA e RR initial data
│   │   └── migrations/
│   ├── config/             # Django settings
│   ├── static/             # CSS, JS, assets
│   └── manage.py
│
├── .claude/                # 🤖 Contexto para AI assistants
│   └── claude.md           # Este ficheiro!
│
├── docs/                   # 📚 Documentation (ver aqui para detalhes!)
│   ├── SOCIOS_MIGRATION.md
│   ├── SALDOS_DASHBOARD.md
│   ├── DATABASE_MANUAL_CHANGES.md
│   └── README.md           # Índice de documentação
│
├── scripts/                # SQL scripts manuais
│   ├── create_socios_table.sql
│   └── add_socio_fk_columns.sql
│
├── backups/                # Database backups
├── excel/                  # Ficheiros Excel para import
├── media/                  # Logos e media files
│
├── docker-compose.yml      # Production compose file
├── deploy.sh               # Deployment script
├── .env                    # Environment variables
├── README.md               # Project overview
└── README-DEV.md           # 📖 Development workflow guide

archive-old-tkinter-app/    # 📦 Old Tkinter app (histórico)
```

---

## 🎯 Core Concepts

### Sócios (Partners)
- **BA** (Bruno Amaral) e **RR** (Rafael Reigota)
- Participação 50/50
- Modelo: `core.models.Socio`
- Campos: codigo (PK: 'BA'/'RR'), nome_completo, email, percentagem_participacao, cor_tema

### Saldos Pessoais (Personal Balances)
**Conceito:** Sócios fazem trabalho freelance mas faturam pela empresa → empresa fica a dever dinheiro aos sócios.

**Fórmula Base:**
```
Saldo = INs - OUTs

INs (empresa DEVE ao sócio):
  • Projetos pessoais (Projeto.tipo = PESSOAL, owner = BA/RR, estado = PAGO)
  • Prémios em projetos da empresa (premio_bruno/premio_rafael, estado = PAGO)
  • A Receber: Projetos/prémios com estado = FINALIZADO (não faturados ainda)

OUTs (empresa PAGOU ao sócio):
  • Despesas fixas mensais ÷ 2 (Despesa.tipo = FIXA_MENSAL, estado = PAGO)
  • Boletins pagos (Boletim.estado = PAGO)
  • Boletins pendentes (Boletim.estado = PENDENTE)
  • Despesas pessoais (Despesa.tipo = PESSOAL_BA/PESSOAL_RR, estado = PAGO)

Nota: Investimento inicial (€5.200/sócio) está documentado no código mas NÃO conta
      no cálculo - é apenas referência histórica.
```

**Dashboard Structure:**
- **Saldos Totais (All-Time):** Mostra saldo projetado acumulado desde sempre para BA e RR
- **Breakdown Anual:** Detalhes do ano corrente com:
  - INs Pagos vs A Receber (finalizados)
  - OUTs Pagos vs Por Pagar (boletins pendentes)
  - Saldo Efetivo (só valores pagos) vs Saldo Projetado (com pendentes)
  - Sugestão de Boletim (baseada no saldo projetado ÷ meses restantes)

**Implementação:**
- Calculator: `core/utils/saldos.py` - classe `SaldosCalculator`
  - `calcular_saldo_bruno()` / `calcular_saldo_rafael()` → saldo total all-time
  - `calcular_saldo_ano(socio, ano)` → breakdown detalhado do ano
- Dashboard: `/admin/core/saldo/` - proxy model `Saldo` (sem tabela)
- Template: `core/templates/admin/core/saldo/changelist.html`
- Admin View: `SaldoAdmin.changelist_view()` em `core/admin.py`

---

## 🌐 Infraestrutura & Deployment

### Arquitetura de Rede
```
Internet
  ↓
Cloudflare (DNS + CDN + SSL Certificate)
  ↓
Server IP (porta 80/443)
  ↓
Traefik v3.3.1 (Reverse Proxy)
  ↓
Docker Network: traefik_proxy
  ↓
agora_web container (Django + Gunicorn :8000)
  ↓
Docker Network: agora_internal
  ↓
agora_db container (PostgreSQL 16 :5432)
```

### Componentes

**Cloudflare:**
- DNS: app.agoramediaproduction.pt → IP do servidor
- Proxy Mode: ON (orange cloud)
- SSL/TLS: Full (certificate on origin)
- Não usa Cloudflare Tunnel!

**Traefik:**
- Container: `traefik:v3.3.1`
- Portas expostas: 80 (HTTP), 443 (HTTPS), 8080 (Dashboard)
- Entrypoints: `http`, `https`
- Cert Resolver: `http` (para Cloudflare compatibility)
- Network: `traefik_proxy` (external)

**Django App:**
- Container: `agora_web`
- Comando: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`
- Networks: `agora_internal` + `traefik_proxy`
- Volume: `agora_web_postgres_data` (IMPORTANTE: nome histórico, não mudar!)

### Server Paths

**Production (e Development):** `/home/zumine/amp/docker/app/`

**NOTA:** Com VS Code Extension, trabalhamos DIRETAMENTE no servidor.
Não há separação entre ambiente local e servidor.

### Environment Variables

**Ficheiro:** `.env` (na raiz do projeto no servidor)

```bash
# Django
DEBUG=False
SECRET_KEY=f#&l*&fzdxbrdttr1rjfn279x-aey=86p%a0a3yxgjj4-@vp12
DJANGO_SETTINGS_MODULE=config.settings

# Domain
DOMAIN=app.agoramediaproduction.pt
ALLOWED_HOSTS=app.agoramediaproduction.pt,localhost,127.0.0.1

# Database (credenciais históricas - não mudar!)
DB_NAME=agora_production
DB_USER=agora
DB_PASSWORD=Agora2025Prod!SecureDB
```

### Branch Strategy

**Production Branch:** `main`
- Sempre estável e deployável
- Merges só após testing

**Feature Branches:** `claude/nome-da-feature-xxxxx`
- Criar nova branch para cada feature/fix
- Testar completamente antes de merge
- Apagar após merge (opcional)

**Naming Convention:**
- `claude/feat-*` - Novas funcionalidades
- `claude/fix-*` - Correções de bugs
- `claude/refactor-*` - Refactoring
- `claude/docs-*` - Atualizações de documentação

---

## 🗄️ Database

**PostgreSQL 16** rodando em Docker.

### Important Tables

| Table | Model | Description |
|-------|-------|-------------|
| `socios` | Socio | Sócios BA e RR (PK: codigo) |
| `projetos` | Projeto | Projetos com FK `socio_id` |
| `despesas` | Despesa | Despesas da empresa |
| `boletins` | Boletim | Recibos verdes com FK `socio_id` |
| `orcamentos` | Orcamento | Orçamentos com FK `socio_id` |

### Migration History

⚠️ **Migration 0004 foi faked** porque incluía tabelas já existentes (Equipamento, Orcamento).

**Consequência:** A tabela `socios` teve de ser criada **manualmente** via SQL.

**Ver:** `docs/DATABASE_MANUAL_CHANGES.md` para detalhes completos.

---

## 🔧 Common Tasks

### Acessar Django Shell
```bash
docker compose exec web python manage.py shell
```

### Ver Logs
```bash
docker compose logs -f web
```

### Aplicar Migrations
```bash
docker compose exec web python manage.py migrate
```

### Criar Superuser
```bash
docker compose exec web python manage.py createsuperuser
```

### Rebuild após Mudanças de Código
```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### Backup da Base de Dados
```bash
docker compose exec db pg_dump -U agora agora_production > "backup_$(date +%Y%m%d_%H%M%S).sql"
```

### Executar SQL Manualmente
```bash
docker compose exec db psql -U agora -d agora_production
```

---

## 🐛 Known Issues & Solutions

### 1. Migration 0004 Faked
**Problema:** Migration incluía tabelas já existentes
**Solução:** `--fake` + criar tabelas manualmente via SQL
**Detalhes:** `docs/DATABASE_MANUAL_CHANGES.md`

### 2. Saldo Proxy Model 500 Error
**Problema:** `super().changelist_view()` tentava query em tabela inexistente
**Solução:** Render template diretamente com `render()` em vez de `super()`
**Commit:** a3276b3

### 3. Docker Code Not Updating
**Problema:** Alterações não aparecem na app
**Solução:** Código está na imagem Docker, não montado como volume → `docker compose up -d --build web`

### 4. PostgreSQL PROTECT vs RESTRICT
**Problema:** SQL com `ON DELETE PROTECT` falha
**Solução:** PostgreSQL usa `RESTRICT` não `PROTECT`

---

## 📝 Recent Major Changes

### ✅ Socio Model Implementation (Dec 2025)
- Created `Socio` model with BA/RR data
- Added ForeignKeys to Projeto, Boletim, Orcamento
- Migrated 81 projects, 37 bulletins, 1 budget
- **Docs:** `docs/SOCIOS_MIGRATION.md`

### ✅ Saldos Pessoais Dashboard (Dec 2025)
- Created `Saldo` proxy model (no database table)
- Custom `SaldoAdmin.changelist_view()` with real-time calculations
- Clean card-based layout (no charts after user feedback)
- **Docs:** `docs/SALDOS_DASHBOARD.md`

---

## 🎨 Admin Customizations

**Theme:** Unfold - modern Django admin theme

**Custom Admins:**
- `SocioAdmin` - shows only codigo in lists (not full name)
- `ProjetoAdmin`, `OrcamentoAdmin`, `BoletimAdmin` - use `socio` FK field
- `SaldoAdmin` - custom dashboard without database queries

**Sidebar Navigation:** Configured in `config/settings.py` - `UNFOLD` dict

---

## 🔐 Environment Variables

**File:** `agora_web/.env.production` (symlinked to `.env`)

**Important vars:**
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - Django secret
- `DEBUG` - Should be False in production
- `ALLOWED_HOSTS` - Domain and localhost

---

## 🚀 Deployment Workflow

**Com VS Code Extension (Workflow Atual):**

1. **Branch:** `git checkout -b claude/feature-xxx`
2. **Develop:** Code changes DIRETAMENTE no servidor
3. **Test:** `docker compose up -d --build web`
4. **Commit:** `git commit -m "feat: descrição"`
5. **Push:** `git push -u origin claude/feature-xxx`
6. **Merge:** `git checkout main && git pull && git merge claude/feature-xxx && git push`
7. **Deploy:** `./deploy.sh` (já estamos no servidor!)
8. **Verify:** Testar em https://app.agoramediaproduction.pt

**Vantagem:** Sem sincronização entre ambientes! Tudo numa máquina só.

---

## 💡 Tips for AI Assistants

### Workflow com VS Code Extension

1. **Estamos NO SERVIDOR** - mudanças são diretas, sem worktrees
2. **Always rebuild Docker** after code changes - código está na imagem
3. **Testar antes de commit** - `docker compose up -d --build web`
4. **Feature branches** - sempre criar branch para cada tarefa
5. **Consulta README-DEV.md** para workflow detalhado

### Desenvolvimento

1. **Check docs/** antes de implementar features existentes
2. **Saldos calculation** é sensível - testar no shell primeiro
3. **Migrations:** Se problemas, considera SQL manual (ver docs)
4. **Template changes:** Também precisam de rebuild Docker
5. **PostgreSQL syntax:** Usa RESTRICT não PROTECT
6. **Commit messages:** Usar prefixos (feat:, fix:, docs:, etc)

---

## 📚 Further Reading

### Documentação Essencial
- **`README-DEV.md`** - ⭐ Workflow de desenvolvimento (VS Code Extension)
- **`docs/SOCIOS_MIGRATION.md`** - Como Socio model foi implementado
- **`docs/SALDOS_DASHBOARD.md`** - Dashboard implementation details
- **`docs/DATABASE_MANUAL_CHANGES.md`** - Manual SQL changes history
- **`docs/README.md`** - Índice completo da documentação
- **`agora_web/README.md`** - Django app specific docs

### Histórico
- **`archive-old-tkinter-app/`** - App antiga (Tkinter + SQLite) - apenas referência

---

**Last Updated:** 2026-01-03
**Project Status:** ✅ Production Ready
**Production Branch:** `main`
**Workflow:** VS Code Extension (direto no servidor)
