from django.urls import path
from .views import PedidoAPIView, CancelarPedidoAPIView

urlpatterns = [
    path('', PedidoAPIView.as_view(), name='pedidos_list_create'),
    path('<int:pedido_id>/cancelar/', CancelarPedidoAPIView.as_view(), name='cancelar_pedido'), 
]