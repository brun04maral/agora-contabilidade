#!/bin/bash
# Run Django Local

echo "🚀 Iniciando Django + Unfold..."

# Ativar venv
source venv/bin/activate

# Usar settings local (SQLite)
export DJANGO_SETTINGS_MODULE=agora_project.settings_local

# Run server
python manage.py runserver
