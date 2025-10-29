"""
Django settings for CoreSync project.
"""
import os
from pathlib import Path
try:
    from decouple import config
    import dj_database_url
except ImportError:
    # Fallback configuration for development
    class config:
        @staticmethod
        def __call__(key, default=None, cast=None):
            import os
            value = os.environ.get(key, default)
            if cast and value:
                return cast(value)
            return value
    
    class dj_database_url:
        @staticmethod
        def parse(url):
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-coresync-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Render.com optimized ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')
if config('RENDER_EXTERNAL_HOSTNAME', default=''):
    ALLOWED_HOSTS.append(config('RENDER_EXTERNAL_HOSTNAME'))
    ALLOWED_HOSTS.extend(['*.onrender.com', 'coresync.onrender.com'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    # 'django_celery_beat',  # TODO: Activate після pip install
    # 'channels',  # TODO: Activate після pip install
]

LOCAL_APPS = [
    'core',
    'authentication',
    'users',
    'services',
    'memberships',
    'iot_control',
    'payments',
    'forms',
    'analytics',
    'shop',
    'concierge',
    'ai_agent',  # NEW: AI agent з multithreading
    'technicians',  # NEW: Technician portal
    'notifications',  # NEW: Email automation
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# AWS Configuration for Face Recognition
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_REGION = config('AWS_REGION', default='us-east-1')
AWS_REKOGNITION_COLLECTION_ID = config('AWS_REKOGNITION_COLLECTION_ID', default='coresync-members')

# Face Recognition Settings
FACE_RECOGNITION_PROVIDER = config('FACE_PROVIDER', default='local')  # 'aws' or 'local'
FACE_SIMILARITY_THRESHOLD = float(config('FACE_SIMILARITY_THRESHOLD', default='90.0'))
FACE_QUALITY_THRESHOLD = float(config('FACE_QUALITY_THRESHOLD', default='70.0'))
FACE_MAX_IMAGE_SIZE_MB = int(config('FACE_MAX_IMAGE_SIZE_MB', default='5'))

# IoT Control Settings
IOT_CONTROL_ENABLED = config('IOT_CONTROL_ENABLED', default=True, cast=bool)
IOT_WEBSOCKET_TIMEOUT = int(config('IOT_WEBSOCKET_TIMEOUT', default='300'))
IOT_MAX_DEVICES_PER_LOCATION = int(config('IOT_MAX_DEVICES_PER_LOCATION', default='50'))
IOT_COMMAND_RATE_LIMIT = int(config('IOT_COMMAND_RATE_LIMIT', default='100'))  # commands per minute

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
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

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) - WhiteNoise optimized
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise Configuration for Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Favicon Configuration
WHITENOISE_STATIC_PREFIX = '/static/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'CoreSync API',
    'DESCRIPTION': 'API documentation for CoreSync Spa Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# QuickBooks Configuration  
QUICKBOOKS_CLIENT_ID = config('QUICKBOOKS_CLIENT_ID', default='')
QUICKBOOKS_CLIENT_SECRET = config('QUICKBOOKS_CLIENT_SECRET', default='')
QUICKBOOKS_REDIRECT_URI = config('QUICKBOOKS_REDIRECT_URI', default='')

# Redis Configuration for Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://localhost:6379/0')],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/New_York'  # EST timezone
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task

# Celery Beat uses database scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Beat Schedule for QuickBooks auto-sync
CELERY_BEAT_SCHEDULE = {
    'sync-quickbooks-queue': {
        'task': 'payments.tasks.sync_quickbooks_queue',
        'schedule': 300.0,  # Every 5 minutes
        'options': {'max_retries': 3}
    },
    'retry-failed-quickbooks-syncs': {
        'task': 'payments.tasks.retry_failed_quickbooks_syncs',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-sync-records': {
        'task': 'payments.tasks.cleanup_old_sync_records',
        'schedule': 86400.0,  # Daily
    },
}

# Email Configuration - SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY', default='')
DEFAULT_FROM_EMAIL = 'info@coresync.life'
SERVER_EMAIL = 'info@coresync.life'

# QuickBooks API Configuration
QUICKBOOKS_CLIENT_ID = config('QUICKBOOKS_CLIENT_ID', default='')
QUICKBOOKS_CLIENT_SECRET = config('QUICKBOOKS_CLIENT_SECRET', default='')
QUICKBOOKS_ACCESS_TOKEN = config('QUICKBOOKS_ACCESS_TOKEN', default='')
QUICKBOOKS_REFRESH_TOKEN = config('QUICKBOOKS_REFRESH_TOKEN', default='')
QUICKBOOKS_COMPANY_ID = config('QUICKBOOKS_COMPANY_ID', default='')
QUICKBOOKS_SANDBOX = config('QUICKBOOKS_SANDBOX', default=True, cast=bool)  # Set to False for production

# Atlas AI Configuration
ATLAS_API_KEY = config('ATLAS_API_KEY', default='')
ATLAS_WEBHOOK_SECRET = config('ATLAS_WEBHOOK_SECRET', default='')
ATLAS_BASE_URL = config('ATLAS_BASE_URL', default='https://api.youratlas.com/v1')

# Google Services Configuration (будуть додані коли payment card готовий)
GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE = config('GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE', default='')
GOOGLE_SHEETS_SERVICE_ACCOUNT_FILE = config('GOOGLE_SHEETS_SERVICE_ACCOUNT_FILE', default='')

# Sentry Monitoring
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment='production' if not DEBUG else 'development',
    )

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Additional security for production
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True

# Render.com specific optimizations
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
