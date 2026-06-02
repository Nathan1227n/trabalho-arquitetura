from django.urls import path
from .views import ProcessarPagamentoView, PagamentoStatusView

urlpatterns = [
    path('processar/', ProcessarPagamentoView.as_view(), name='processar_pagamento'),
    path('status/<int:order_id>/', PagamentoStatusView.as_view(), name='pagamento_status'),
]
