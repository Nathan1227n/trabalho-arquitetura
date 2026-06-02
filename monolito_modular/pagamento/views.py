from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import PagamentoService


class PagamentoHealthView(APIView):
    def get(self, request):
        return Response(
            {"status": "ok", "service": "pagamento"},
            status=status.HTTP_200_OK,
        )


class PagamentoStatusView(APIView):
    def get(self, request, pedido_id: int):
        status_pagamento = PagamentoService.consultar_status(pedido_id)
        if status_pagamento is None:
            return Response(
                {"erro": "Pagamento não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"pedido_id": pedido_id, "status": status_pagamento},
            status=status.HTTP_200_OK,
        )
