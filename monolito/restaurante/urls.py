from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cardapio', views.CardapioViewSet, basename='cardapio')
router.register(r'pedidos', views.PedidoViewSet, basename='pedido')
router.register(r'notificacoes', views.NotificacaoViewSet, basename='notificacao')
router.register(r'pagamentos', views.PagamentoViewSet, basename='pagamento')

urlpatterns = [
    path('', include(router.urls)),
]