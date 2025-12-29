#!/bin/bash
# Setup Local - Django + Unfold (SQLite)

echo "🚀 Setup Django + Unfold (Local - SQLite)"
echo "=========================================="

# 1. Criar venv
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências (sem PostgreSQL)
echo "📥 Instalando dependências..."
cat > requirements-local.txt << 'EOF'
Django==5.0.0
django-unfold==0.20.0
python-dotenv==1.0.0
djangorestframework==3.14.0
pillow==10.1.0
EOF

pip install -r requirements-local.txt

# 3. Configurar para SQLite
echo "🗄️  Configurando SQLite..."
cat > agora_project/settings_local.py << 'EOF'
from .settings import *

# Override para SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEBUG = True
ALLOWED_HOSTS = ['*']
EOF

# 4. Criar DB
echo "🔨 Criando base de dados..."
export DJANGO_SETTINGS_MODULE=agora_project.settings_local
python manage.py makemigrations agora_app
python manage.py migrate

# 5. Criar superuser
echo ""
echo "👤 Criar utilizador admin:"
python manage.py createsuperuser

echo ""
echo "✅ Setup completo!"
echo ""
echo "🚀 Para iniciar:"
echo "   source venv/bin/activate"
echo "   export DJANGO_SETTINGS_MODULE=agora_project.settings_local"
echo "   python manage.py runserver"
echo ""
echo "📱 Aceder: http://localhost:8000/admin/"
