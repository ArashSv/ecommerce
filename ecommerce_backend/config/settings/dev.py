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