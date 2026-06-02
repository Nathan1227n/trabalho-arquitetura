import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('notificacao')

# Le toda a configuracao CELERY_* do settings do Django.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente os modulos tasks.py dos apps instalados.
app.autodiscover_tasks()
