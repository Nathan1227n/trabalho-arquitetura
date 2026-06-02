from django.urls import path
from .views import PedidoAPIView, PedidoDetailAPIView

urlpatterns = [
    path('', PedidoAPIView.as_view(), name='criar_listar_pedidos'),
    path('<int:pedido_id>/', PedidoDetailAPIView.as_view(), name='detalhe_cancelar_pedido'),
]