from django.urls import path
from .views import PedidoAPIView, PedidoDetailAPIView, CancelarPedidoAPIView

urlpatterns = [
    path('', PedidoAPIView.as_view(), name='criar_listar_pedidos'),
    path('<int:pedido_id>/', PedidoDetailAPIView.as_view(), name='detalhe_cancelar_pedido'),
    path('<int:pedido_id>/cancelar/', CancelarPedidoAPIView.as_view(), name='cancelar_pedido'),
]
