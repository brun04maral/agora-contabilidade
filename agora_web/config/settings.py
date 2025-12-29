"""
Django settings for Agora Contabilidade project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production'))
DEBUG = os.getenv('DEBUG', os.getenv('DJANGO_DEBUG', 'True')) == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', os.getenv('DJANGO_ALLOWED_HOSTS', '*')).split(',')

# Proxy/Cloudflare settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = ['https://app.agoramediaproduction.pt']

# Application definition
INSTALLED_APPS = [
    # Unfold (MUST be before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',

    # Local apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# TEMPORARY: Using SQLite for local development (Docker not available)
# TODO: Switch back to PostgreSQL when deploying with Docker
# Database configuration - auto-detect PostgreSQL or SQLite
if os.getenv('DB_HOST'):
    # PostgreSQL (Docker/Production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'agora_web'),
            'USER': os.getenv('DB_USER', 'agora'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'agora123'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # SQLite (Local development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "Agora Contabilidade",
    "SITE_HEADER": "Agora Media Production",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "https://img.icons8.com/fluency/48/accounting.png",
        "dark": lambda request: "https://img.icons8.com/fluency/48/accounting.png",
    },
    "COLORS": {
        "primary": {
            "50": "250 245 230",  # Dourado claro
            "100": "245 230 180",
            "200": "240 210 130",
            "300": "230 190 80",
            "400": "220 170 50",
            "500": "212 175 55",  # Dourado Agora
            "600": "180 140 40",
            "700": "150 110 30",
            "800": "120 85 20",
            "900": "90 60 10",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "items": [
                    {
                        "title": "Visão Geral",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Financeiro",
                "items": [
                    {
                        "title": "Saldos Pessoais",
                        "icon": "account_balance",
                        "link": "/admin/core/saldo/",
                    },
                    {
                        "title": "Projetos",
                        "icon": "work",
                        "link": "/admin/core/projeto/",
                    },
                    {
                        "title": "Despesas",
                        "icon": "payments",
                        "link": "/admin/core/despesa/",
                    },
                    {
                        "title": "Boletins",
                        "icon": "receipt_long",
                        "link": "/admin/core/boletim/",
                    },
                ],
            },
            {
                "title": "Gestão",
                "items": [
                    {
                        "title": "Orçamentos",
                        "icon": "description",
                        "link": "/admin/core/orcamento/",
                    },
                    {
                        "title": "Clientes",
                        "icon": "people",
                        "link": "/admin/core/cliente/",
                    },
                    {
                        "title": "Fornecedores",
                        "icon": "store",
                        "link": "/admin/core/fornecedor/",
                    },
                    {
                        "title": "Equipamento",
                        "icon": "inventory",
                        "link": "/admin/core/equipamento/",
                    },
                ],
            },
        ],
    },
}
