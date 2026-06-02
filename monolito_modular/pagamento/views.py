from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Transacao


class PagamentoHealthView(APIView):
    def get(self, request):
        return Response(
            {"status": "ok", "service": "pagamento"},
            status=status.HTTP_200_OK,
        )


class PagamentoStatusView(APIView):
    def get(self, request, pedido_id: int):
        transacao = Transacao.objects.filter(pedido_id=pedido_id).first()
        if transacao is None:
            return Response(
                {"erro": "Pagamento não encontrado para este pedido."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "pedido_id": transacao.pedido_id,
                "status": transacao.status,
                "status_pagamento": transacao.status,
                "valor": transacao.valor,
            },
            status=status.HTTP_200_OK,
        )
