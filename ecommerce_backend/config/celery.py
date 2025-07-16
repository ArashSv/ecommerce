import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from celery import Celery
from django.apps import apps

app = Celery("ecommerce_backend")
app.config_from_object("config.settings", namespace="CELERY")
app.autodiscover_tasks()
