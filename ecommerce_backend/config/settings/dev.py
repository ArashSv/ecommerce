from .base import *

DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY = 'django-insecure-a_#o+h-wc^%*dw-7u(*tyx1p0g$pnqjq@gkcbo2pjk(pw**)+2'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# celery development settings
INSTALLED_APPS += ["django_celery_results"]
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "django-db"

# redis dev settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0