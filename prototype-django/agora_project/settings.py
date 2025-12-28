"""
Django settings for Agora Contabilidade project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-prototype-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'unfold',  # Unfold theme - MUST be before django.contrib.admin
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.import_export',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'agora_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agora_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'agora_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'agora_db'),
        'USER': os.getenv('POSTGRES_USER', 'agora'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'agora123'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Unfold Admin Configuration
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
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
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
                "title": "Gestão Financeira",
                "items": [
                    {
                        "title": "Projetos",
                        "icon": "work",
                        "link": "/admin/agora_app/projeto/",
                    },
                    {
                        "title": "Despesas",
                        "icon": "payments",
                        "link": "/admin/agora_app/despesa/",
                    },
                    {
                        "title": "Saldos",
                        "icon": "account_balance",
                        "link": "/admin/agora_app/socio/",
                    },
                ],
            },
            {
                "title": "Cadastros",
                "items": [
                    {
                        "title": "Clientes",
                        "icon": "people",
                        "link": "/admin/agora_app/cliente/",
                    },
                    {
                        "title": "Fornecedores",
                        "icon": "store",
                        "link": "/admin/agora_app/fornecedor/",
                    },
                ],
            },
        ],
    },
}
