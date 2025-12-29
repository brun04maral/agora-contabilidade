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

## Próximos Passos

- [ ] Migrar models (Cliente, Fornecedor, Projeto, Despesa, Boletim)
- [ ] Adaptar SaldosCalculator
- [ ] Django Admin customizado
- [ ] Dashboard com saldos
- [ ] Relatórios/exports

## Docs

Ver `../DJANGO_IMPLEMENTATION_PLAN.md` para roadmap completo.
