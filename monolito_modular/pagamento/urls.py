from django.urls import path
from .views import PagamentoHealthView, PagamentoStatusView

urlpatterns = [
    path('health/', PagamentoHealthView.as_view(), name='pagamento_health'),
    path('status/<int:pedido_id>/', PagamentoStatusView.as_view(), name='pagamento_status'),
    path('<int:pedido_id>/', PagamentoStatusView.as_view(), name='consultar_pagamento'),
]
