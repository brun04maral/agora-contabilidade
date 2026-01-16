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

### ⚠️ REGRA IMPORTANTE: Unfold Documentation First
**Sempre que fizeres alterações ao Unfold:**
1. **Consulta PRIMEIRO a documentação oficial:** https://unfoldadmin.com/docs/
2. **Se não houver documentação sobre o tema:** Pesquisa na web (GitHub issues, Stack Overflow, etc.)
3. **Nunca assumes** - verifica sempre a sintaxe correta antes de implementar

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

**Lógica Dual (v2.1):**

**SALDO ATUAL** (decisões financeiras HOJE):
```
INs (empresa DEVE ao sócio):
  • Projetos pessoais PAGOS (data_recibo exists)
  • Prémios de trabalho FEITO (data_fim < hoje)

OUTs (empresa PAGOU ao sócio):
  • Despesas fixas mensais ÷ 2 (tags: ADMINISTRATIVO, ORDENADO, SUB_ALIMENTACAO)
  • Boletins PAGOS (estado=PAGO)
  • Despesas pessoais (tag: PESSOAL)

Saldo Atual = INs (trabalho feito) - OUTs (pagos)
```

**SALDO PROJETADO** (planeamento médio prazo):
```
INs (empresa DEVE ou VAI DEVER ao sócio):
  • Projetos pessoais PAGOS (data_recibo exists)
  • Prémios de TODOS os projetos (incluindo futuros agendados)

OUTs (empresa PAGOU ou VAI PAGAR ao sócio):
  • Despesas fixas mensais ÷ 2
  • Boletins TODOS (PAGO + PENDENTE - já declarados às finanças)
  • Despesas pessoais todas

Saldo Projetado = INs (incluindo futuros) - OUTs (incluindo pendentes)
```

**Nota:** Investimento inicial (€5.200/sócio) está documentado mas NÃO conta no cálculo.

**Dashboard Structure:**
- **Saldos Totais:** Mostra saldo atual e projetado acumulado desde sempre
- **Breakdown Anual:** Detalhes do ano corrente com filtros de data
- **Sugestão de Boletim:** Baseada no saldo projetado ÷ meses restantes sem boletim

**Implementação:**
- Calculator: `core/utils/saldos.py` - classe `SaldosCalculator`
  - `calcular_saldo_bruno(incluir_investimento, data_inicio, data_fim)` → dict com ambos os saldos
  - `calcular_saldo_rafael(incluir_investimento, data_inicio, data_fim)` → dict com ambos os saldos
  - Retorna sempre: `saldo_atual`, `saldo_projetado`, `ins`, `outs`, `sugestao_boletim`
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
- Branch principal de trabalho
- Commits diretos para agilidade
- Sempre estável (testar antes de push!)

**Feature Branches:** Opcionais
- Usar **apenas** para experimentação arriscada ou features grandes (dias/semanas)
- Na maioria dos casos: trabalhar direto em `main`
- Se usar: `claude/feat-*`, `claude/fix-*`, `claude/refactor-*`, `claude/docs-*`

**Workflow Atual (Simplificado):**
1. `git pull origin main`
2. Fazer mudanças + testar
3. `git add . && git commit -m "feat: descrição"`
4. `git push origin main`

**Quando usar branches:**
- 🔬 Experimentação que pode quebrar sistema
- 🚧 Features grandes multi-commit
- 👥 Colaboração simultânea em features diferentes

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

### Current State (03 Jan 2026)

**Base de dados sincronizada com Excel CONTABILIDADE_FINAL_20251231.xlsx**:
- **Fornecedores**: 45 (2 com nome NULL não importaram)
- **Clientes**: 18 (2 com nome NULL não importaram)
- **Projetos**: 80 válidos (1,619 vazios removidos após importação)
- **Despesas**: 236 válidas (639 vazias removidas após importação)
- **Boletins**: 24 (agregados por sócio/mês/ano)

---

## 📥 Importação de Dados Excel

**Sistema completo de importação Excel → PostgreSQL (v2.1)**

### Comandos Disponíveis

```bash
# 1. Importar dados do Excel
docker compose exec web python manage.py import_from_excel excel/CONTABILIDADE_FINAL_20251231.xlsx

# 2. Limpar projetos vazios (após importação)
docker compose exec web python manage.py limpar_projetos_vazios --dry-run  # Preview
docker compose exec web python manage.py limpar_projetos_vazios            # Real

# 3. Limpar despesas vazias (após importação)
docker compose exec web python manage.py limpar_despesas_vazias --dry-run  # Preview
docker compose exec web python manage.py limpar_despesas_vazias            # Real

# 4. Auditar importação (comparar Excel vs DB)
docker compose exec web python manage.py auditar_importacao excel/CONTABILIDADE_FINAL_20251231.xlsx

# 5. Analisar fórmulas da aba CAIXA
docker compose exec web python manage.py analisar_caixa excel/CONTABILIDADE_FINAL_20251231.xlsx --output docs/CAIXA_ANALYSIS.md
```

### Como Funciona a Importação

**`import_from_excel.py`** processa 5 abas do Excel:

1. **FORNECEDORES** → modelo `Fornecedor`
2. **CLIENTES** → modelo `Cliente` (exclui sócios #C0001 e #C0002)
3. **PROJETOS** → modelo `Projeto`
4. **DESPESAS** → 3 categorias:
   - Despesas normais → modelo `Despesa`
   - Boletins (ajudas de custo) → **agregados** por (sócio, mês, ano) → modelo `Boletim`
   - Prémios → **agregados** por projeto → campos `premio_bruno`/`premio_rafael` em `Projeto`

**Agregação de Prémios:**
```python
# Excel tem múltiplas linhas de prémio para o mesmo projeto
# Importação soma e popula campos premio_bruno/premio_rafael

Exemplo:
  Excel linha 125: Prémio Bruno #P0032 = €225.00
  Excel linha 184: Prémio Bruno #P0032 = €225.00
  → DB: Projeto.premio_bruno = €450.00
```

**Agregação de Boletins:**
```python
# Excel tem linhas individuais de ajudas de custo
# Importação agrupa por (sócio, mês, ano) em Boletim único

Exemplo:
  Excel: 56 linhas de "Deslocação, Pessoal" em 2025
  → DB: 24 boletins (2 sócios × 12 meses)
```

**Sistema de Tags (Despesas):**
```python
# Substituiu enums TipoDespesa por sistema flexível de tags
Tags disponíveis:
  - EQUIPAMENTO, PROJETO, PESSOAL, FIXA_MENSAL
  - ADMINISTRATIVO, ORDENADO, SUB_ALIMENTACAO
  - DESLOCACAO, PER_DIEM_PT, PER_DIEM_FORA
  - PREMIO, COMISSAO
```

**Ver:** `docs/EXCEL_IMPORT_ANALYSIS.md` para análise completa do Excel.

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
# ⚠️ SEMPRE usar --build quando alterar código Python (settings.py, models.py, admin.py, etc)
docker compose up -d --build web

# Se mudanças em static files (CSS/JS):
docker compose exec web python manage.py collectstatic --noinput

# Rebuild completo (raramente necessário):
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

### 4. Cache Busting Not Working (Static Files)
**Problema:** Alterações em CSS/JS não aparecem no browser mesmo após Cloudflare cache purge
**Root Cause:** `docker compose restart web` NÃO copia código atualizado para o container
**Solução CORRETA:**
```bash
# ❌ ERRADO - não atualiza código Python dentro do container
docker compose restart web

# ✅ CERTO - rebuild da imagem com código atualizado
docker compose up -d --build web
docker compose exec web python manage.py collectstatic --noinput
```

**⚠️ CRÍTICO:** Quando alterar `settings.py` (ou qualquer ficheiro Python):
1. SEMPRE usar `--build` flag
2. Cache busting só funciona se o settings.py no container tiver a versão correta
3. Testar com: `docker compose exec web python manage.py shell -c "from config.settings import get_custom_css; ..."`

**Histórico:** 16 Jan 2026 - Cache busting timestamp não aplicado porque restart não copiou settings.py

### 5. PostgreSQL PROTECT vs RESTRICT
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

**Com VS Code Extension (Workflow Atual - Simplificado):**

1. **Sync:** `git pull origin main`
2. **Develop:** Code changes DIRETAMENTE no servidor
3. **Test:** `docker compose up -d --build web`
4. **Commit:** `git add . && git commit -m "feat: descrição"`
5. **Push:** `git push origin main` (direto para produção!)
6. **Verify:** Testar em https://app.agoramediaproduction.pt

**Vantagens:**
- ✅ Sem sincronização entre ambientes! Tudo numa máquina só
- ✅ Sem overhead de branches para tasks pequenas/médias
- ✅ Deploy contínuo e ágil

**Nota:** Branches opcionais para experimentação arriscada (ver "Branch Strategy" acima).

---

## 💡 Tips for AI Assistants

### Workflow com VS Code Extension

1. **Estamos NO SERVIDOR** - mudanças são diretas, sem worktrees
2. **Always rebuild Docker** after code changes - código está na imagem
3. **Testar antes de push** - `docker compose up -d --build web`
4. **Commit direto em main** - workflow simplificado para agilidade
5. **Branches opcionais** - apenas para experimentação arriscada
6. **Consulta README-DEV.md** para workflow detalhado

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
