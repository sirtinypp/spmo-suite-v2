"""
Django settings for config project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-LOCAL-DEV-FALLBACK-ONLY-90glx')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

# Allow all hosts so Docker networking works smoothly
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

# CSRF Configuration - Read from environment or use production defaults
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://lipad-sspmo.up.edu.ph',
        'http://lipad-sspmo.up.edu.ph',
        'http://localhost:8002',
        'http://localhost',
        'http://127.0.0.1:8002',
        'http://127.0.0.1'
    ]

# ... skipped ...

# 1. Enforce SSL/HTTPS
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL', 'False') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 # 1 Year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 2. Harden Cookies
SESSION_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'False') == 'True'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'travel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise
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
        'DIRS': [BASE_DIR / 'templates'], # Looks for templates in root/templates
        'APP_DIRS': True, # Also looks inside travel/templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.sspmo_hub_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with PostgreSQL if environment variables are present (Docker/Production)
if os.environ.get('DB_NAME') and os.environ.get('DB_HOST'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- MEDIA FILES (Tickets/Uploads) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Allow larger file uploads (e.g., 10MB) for scanned PDFs
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760 

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AUTHENTICATION & SESSION SETTINGS ---
LOGIN_URL = 'login'             
LOGIN_REDIRECT_URL = 'index' # Changed from 'landing_page' to match urls.py 'name=index'
LOGOUT_REDIRECT_URL = 'login'

# Session Timeout Logic
SESSION_COOKIE_AGE = 600 # 10 Minutes (in seconds)
SESSION_SAVE_EVERY_REQUEST = True # Reset timer on activity
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Logout when browser closes

# --- SSPMO HUB URL ---
SSPMO_HUB_URL = os.environ.get('SSPMO_HUB_URL', 'https://sspmo.up.edu.ph')


# ... (bottom of file)

# --- EMAIL SETTINGS ---
# For Development: Prints emails to the terminal/console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For Production (When ready, replace above with this):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@up.edu.ph'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'SPMO GFA System <no-reply@up.edu.ph>'

