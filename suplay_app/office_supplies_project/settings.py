"""
Django settings for office_supplies_project project.
"""

import os  # <--- CRITICAL: Required to read Docker environment variables
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-spc7#!k=$cb8azdidp*jflg7(_6_#scd7^e=lmww_b1!sqxn2h",
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True  # Moved to line 181 (environment-controlled)

# Allow all hosts so Docker containers can talk to each other
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "suplay-sspmo.up.edu.ph,localhost,127.0.0.1"
).split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "supplies",  # Your App
    "import_export",  # For Excel import/export
    "django.contrib.humanize",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <--- CRITICAL: Handles CSS in Docker
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "office_supplies_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "office_supplies_project.wsgi.application"


# Database
# Connects to the Docker Container named 'db' using variables from docker-compose.yml

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DB_NAME"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": "5432",
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATICFILES_DIRS = []  # Added to satisfy WhiteNoise in some configurations if needed

# Where to collect static files (Required for WhiteNoise)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Enable WhiteNoise storage to ensure CSS loads cleanly
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (User uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB in bytes
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB in bytes

# Login/Logout Redirect Settings
LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"
LOGOUT_REDIRECT_URL = "login"

# --- SESSION TIMEOUT SETTINGS ---
SESSION_COOKIE_AGE = 600  # 10 minutes of inactivity (changed from 3000)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Allow Docker to handle CSRF tokens
# Allow Docker to handle CSRF tokens
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8003",
    "http://127.0.0.1:8003",
    "http://10.10.5.13:8003",
    "https://suplay-sspmo.up.edu.ph",
    "http://suplay-sspmo.up.edu.ph",
]

# ==============================================================================
# --- SECURITY HARDENING (DAST REMEDIATION) ---
# ==============================================================================

# 1. Enforce SSL/HTTPS
# 1. Enforce SSL/HTTPS
SECURE_SSL_REDIRECT = False  # Disabled for HTTP Nginx setup
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 0  # Disabled for rollback
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 2. Harden Cookies
SESSION_COOKIE_SECURE = False  # Disabled for HTTP
CSRF_COOKIE_SECURE = False  # Disabled for HTTP
SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False # Kept False for AJAX/HTMX compatibility

# 3. Mitigate Referrer Leakage
SECURE_REFERRER_POLICY = "same-origin"

# 4. Production Readiness
# DEBUG = False
DEBUG = os.environ.get("DEBUG") == "True"

# 5. Ensure WhiteNoise (Logic verifies existing config)
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
