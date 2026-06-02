from django.urls import path
from .views import NotificacaoHealthView

urlpatterns = [
    path('health/', NotificacaoHealthView.as_view(), name='notificacao_health'),
]
