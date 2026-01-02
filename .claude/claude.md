# Agora Contabilidade - Claude Code Context

## 📋 Overview

Sistema de contabilidade Django para **Amaral & Reigota - Produção Audiovisual, Lda**
- **NIPC:** 518 351 190
- **Marca:** Agora Media Production
- **Sócios:** Bruno Amaral (BA) e Rafael Reigota (RR)

**Tech Stack:**
- Django 5.0 + PostgreSQL 16
- Unfold Admin Theme
- Docker + Cloudflare Tunnel
- Python 3.11

**Deployment:** Production via Docker Compose com Cloudflare tunnel para acesso remoto.

---

## 🏗️ Arquitetura

```
agora-contabilidade/
├── agora_web/              # Django application (trabalha aqui!)
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
│   └── manage.py
│
├── scripts/                # SQL scripts manuais
│   ├── create_socios_table.sql
│   └── add_socio_fk_columns.sql
│
├── docs/                   # 📚 Documentation (ver aqui para detalhes!)
│   ├── SOCIOS_MIGRATION.md
│   ├── SALDOS_DASHBOARD.md
│   └── DATABASE_MANUAL_CHANGES.md
│
└── docker-compose.cloudflare.yml  # Production compose file
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
docker compose -f docker-compose.cloudflare.yml exec web python manage.py shell
```

### Ver Logs
```bash
docker compose -f docker-compose.cloudflare.yml logs -f web
```

### Aplicar Migrations
```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py migrate
```

### Criar Superuser
```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py createsuperuser
```

### Rebuild após Mudanças de Código
```bash
docker compose -f docker-compose.cloudflare.yml up -d --build web
```

### Executar SQL Manualmente
```bash
docker compose -f docker-compose.cloudflare.yml exec db psql -U agora_user -d agora_db -f /path/to/script.sql
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

1. **Development:** Code changes in local/Claude worktree
2. **Commit:** `git commit -m "message"`
3. **Push:** `git push -u origin <branch>`
4. **Server:** `git pull origin <branch>`
5. **Rebuild:** `docker compose -f docker-compose.cloudflare.yml up -d --build web`
6. **Verify:** Check logs and test functionality

**Note:** Server has Cloudflare tunnel configured - acessível remotamente.

---

## 💡 Tips for AI Assistants

1. **Always rebuild Docker** after code changes - não há volume mount
2. **Check docs/** antes de implementar features existentes
3. **Saldos calculation** é sensível - testar sempre no shell primeiro
4. **Migrations:** Se encontrares problemas, considera SQL manual (ver docs)
5. **Template changes:** Também precisam de rebuild Docker
6. **PostgreSQL syntax:** Usa RESTRICT não PROTECT

---

## 📚 Further Reading

- `docs/SOCIOS_MIGRATION.md` - Como Socio model foi implementado
- `docs/SALDOS_DASHBOARD.md` - Dashboard implementation details
- `docs/DATABASE_MANUAL_CHANGES.md` - Manual SQL changes history
- `agora_web/README.md` - Django app specific docs

---

**Last Updated:** 2025-12-29
**Project Status:** ✅ Production Ready
**Current Branch:** `claude/self-hosted-brainstorm-heo8m`
