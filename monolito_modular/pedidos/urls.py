from django.urls import path
from .views import PedidoAPIView

urlpatterns = [
    path('', PedidoAPIView.as_view(), name='criar_pedido'),
]