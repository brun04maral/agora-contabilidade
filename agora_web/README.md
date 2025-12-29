# 🚀 Agora Web - Django + Unfold

Versão web da aplicação Agora Contabilidade.

## Stack

- **Backend:** Django 5.0 (Python 3.12)
- **UI:** Django Admin + Unfold theme
- **Database:** PostgreSQL 16
- **Deploy:** Docker Compose

## Quick Start

### Docker (Recomendado)

```bash
cd agora_web

# Iniciar
docker-compose up --build

# Criar superuser (noutra tab)
docker-compose exec web python manage.py createsuperuser

# Acessar
# http://localhost:8001/admin/
```

### Local (sem Docker)

```bash
cd agora_web

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar deps
pip install -r requirements.txt

# Configurar .env (copiar de .env.example)
cp .env.example .env

# Migrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser

# Run
python manage.py runserver

# Acessar: http://localhost:8000/admin/
```

## Estrutura

```
agora_web/
├── config/           # Settings Django
│   ├── settings.py  # Configuração principal
│   ├── urls.py      # Rotas
│   └── wsgi.py
│
├── core/            # App principal
│   ├── models.py    # Models (migrando de SQLAlchemy)
│   ├── admin.py     # Django Admin customizado
│   └── utils/       # Saldos calculator, etc
│
├── manage.py        # Django CLI
├── requirements.txt
└── docker-compose.yml
```

## ✅ Implemented Features

- ✅ **Models completos:** Cliente, Fornecedor, Projeto, Despesa, Boletim, Equipamento, Orcamento, Socio
- ✅ **SaldosCalculator:** Cálculo em tempo real de saldos pessoais (BA/RR)
- ✅ **Django Admin:** Customizado com Unfold theme
- ✅ **Dashboard Saldos Pessoais:** `/admin/core/saldo/` - visualização em tempo real
- ✅ **Modelo Socio:** Integração de sócios (BA/RR) com ForeignKeys
- ✅ **Docker Deployment:** Production-ready com Cloudflare Tunnel

## 📚 Documentation

**Comprehensive docs available:**

### For AI Assistants & Quick Context
- **[`.claude/claude.md`](../.claude/claude.md)** - Complete project context, architecture, common tasks

### For Developers
- **[`docs/README.md`](../docs/README.md)** - Documentation index
- **[`docs/SOCIOS_MIGRATION.md`](../docs/SOCIOS_MIGRATION.md)** - Socio model implementation guide
- **[`docs/SALDOS_DASHBOARD.md`](../docs/SALDOS_DASHBOARD.md)** - Saldos dashboard deep dive
- **[`docs/DATABASE_MANUAL_CHANGES.md`](../docs/DATABASE_MANUAL_CHANGES.md)** - Manual SQL changes history

### Quick Reference
```bash
# Common commands
docker compose -f docker-compose.cloudflare.yml exec web python manage.py shell
docker compose -f docker-compose.cloudflare.yml logs -f web
docker compose -f docker-compose.cloudflare.yml up -d --build web

# Load initial Socio data
docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata socios

# Migrate Socio FKs
docker compose -f docker-compose.cloudflare.yml exec web python manage.py migrate_socios
```

## 🎯 Current Status

**Production Ready** ✅ - Deployed with Docker + PostgreSQL + Cloudflare Tunnel

**Last Major Updates (Dec 2025):**
- Socio model with ForeignKey relationships
- Saldos Pessoais dashboard with real-time calculations
- Manual database changes documented
