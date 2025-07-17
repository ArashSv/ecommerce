from .base import *
import environ

# -------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    POSTGRES_PORT=(int, 5432),
    REDIS_PORT=(int, 6379),
    REDIS_DB=(int, 0),
)

# -------------------------------------------------------------
# SECURITY
# -------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# -------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("POSTGRES_DB"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("POSTGRES_HOST"),
        'PORT': env.int("POSTGRES_PORT"),
    }
}

# -------------------------------------------------------------
# CELERY
# -------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

# -------------------------------------------------------------
# REDIS
# -------------------------------------------------------------
REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env.int("REDIS_PORT")
REDIS_DB = env.int("REDIS_DB")
REDIS_PASSWORD = env("REDIS_PASSWORD")