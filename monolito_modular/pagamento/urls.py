from django.urls import path
from .views import ConsultarPagamentoView

urlpatterns = [
    path('<int:pedido_id>/', ConsultarPagamentoView.as_view(), name='consultar_pagamento'),
]