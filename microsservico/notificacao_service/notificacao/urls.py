from django.urls import path
from .views import NotificacaoListView

urlpatterns = [
    path('', NotificacaoListView.as_view(), name='listar_notificacoes'),
]
