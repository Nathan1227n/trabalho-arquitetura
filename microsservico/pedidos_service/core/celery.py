import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('pedidos')

# Le a configuracao CELERY_* do settings do Django.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Este servico apenas PUBLICA tasks (via send_task) para o servico de
# notificacao; ele nao roda worker e nao tem tasks locais.
