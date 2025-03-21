import os
import dj_database_url
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)  # DEBUG можна керувати через змінну середовища

# ALLOWED_HOSTS: для продакшена потрібно вказати домен вашого додатка на Heroku, наприклад, 'your-app.herokuapp.com'
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost',
                         cast=lambda v: [s.strip() for s in v.split(',')])
# Приклад: ALLOWED_HOSTS = ['your-app.herokuapp.com', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounting',

    'widget_tweaks',
    'django_select2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # додано для обслуговування статичних файлів на Heroku
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sport_accounting.urls'

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

WSGI_APPLICATION = 'sport_accounting.wsgi.application'

# Налаштування бази даних через dj_database_url. Heroku автоматично встановлює DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # Інші валідатори за потребою
]

LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статичні файли:
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # для Heroku бажано використовувати директорію "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # для оптимізації статичних файлів

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FILE_UPLOAD_PERMISSIONS = 0o644

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
