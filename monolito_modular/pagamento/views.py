from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transacao

class ConsultarPagamentoView(APIView):
    def get(self, request, pedido_id):
        try:
            transacao = Transacao.objects.get(pedido_id=pedido_id)
            return Response({
                "pedido_id": transacao.pedido_id,
                "status_pagamento": transacao.status,
                "valor": transacao.valor
            })
        except Transacao.DoesNotExist:
            return Response({"erro": "Pagamento não encontrado para este pedido."}, status=status.HTTP_404_NOT_FOUND)