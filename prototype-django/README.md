# 🎨 Protótipo Django + Unfold

Protótipo da aplicação Agora Contabilidade usando Django com tema Unfold.

## 🚀 Stack

- **Backend:** Django 5.0 (Python)
- **UI:** Django Admin + Unfold Theme
- **Database:** PostgreSQL
- **Deploy:** Docker Compose

## ✨ Features Implementadas

- ✅ Gestão de Sócios (com cálculo de saldos)
- ✅ Gestão de Projetos
- ✅ Gestão de Despesas
- ✅ Gestão de Clientes
- ✅ Gestão de Fornecedores
- ✅ API REST (endpoint saldos)
- ✅ UI moderna com Unfold

## 🏃 Como Rodar

### Opção 1: Docker Compose (Recomendado)

```bash
cd prototype-django

# Build e start
docker-compose up --build

# Criar superuser (em outro terminal)
docker-compose exec web python manage.py createsuperuser

# Acessar
# Admin: http://localhost:8000/admin/
# API: http://localhost:8000/api/saldos/
```

### Opção 2: Local (requer Python 3.12+)

```bash
cd prototype-django

# Criar venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar deps
pip install -r requirements.txt

# Configurar PostgreSQL (ou usar SQLite)
# Editar agora_project/settings.py para SQLite se necessário

# Migrations
python manage.py makemigrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser

# Run
python manage.py runserver

# Acessar: http://localhost:8000/admin/
```

## 📸 Screenshots

### Dashboard Principal
![Dashboard](../screenshots/django-dashboard.png)

### Lista de Projetos
![Projetos](../screenshots/django-projetos.png)

### Saldos dos Sócios
![Saldos](../screenshots/django-saldos.png)

## 🎯 Vantagens

✅ **100% Python** - Zero JavaScript necessário (exceto admin built-in)
✅ **UI Moderna** - Unfold theme = Tailwind-like design
✅ **CRUD Automático** - Django Admin gera forms/tables automaticamente
✅ **Rápido** - Menos código que React
✅ **Battle-tested** - Django = 18 anos de produção
✅ **Self-hosted** - Docker Compose fácil

## ⚠️ Limitações

⚠️ Django Admin = "Admin panel" vibe (não é "app moderna")
⚠️ Customizações profundas = overrides de templates
⚠️ Mobile = responsive mas não é PWA

## 📝 Próximos Passos

Se escolher esta opção:

1. Migrar todos os models (Boletins, Orçamentos, etc)
2. Custom dashboard (não default admin)
3. Relatórios/exports Excel
4. Auth de produção
5. Deploy para servidor

## 🔗 Links Úteis

- Unfold Docs: https://unfoldadmin.com/
- Django Docs: https://docs.djangoproject.com/
