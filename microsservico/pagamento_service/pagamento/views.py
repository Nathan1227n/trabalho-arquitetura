import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PaymentTransaction


class ProcessarPagamentoView(APIView):
    """
    Processa o pagamento (mock).

    Recebe { "order_id": int, "amount": number }, simula a lentidao de um
    gateway real (sleep 5s) e aprova a transacao. Chamado de forma SINCRONA
    pelo servico de pedidos via HTTP.
    """

    def post(self, request):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')

        if order_id is None or amount is None:
            return Response(
                {"erro": "order_id e amount sao obrigatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print(f"Iniciando pagamento do pedido {order_id}...")

        transaction, created = PaymentTransaction.objects.get_or_create(
            order_id=order_id,
            defaults={
                'amount': amount,
                'status': 'PROCESSING',
            },
        )
        if not created:
            transaction.amount = amount
            transaction.status = 'PROCESSING'
            transaction.save(update_fields=['amount', 'status'])

        # Simula a latencia do gateway de pagamento (experimento obrigatorio)
        time.sleep(5)

        transaction.status = 'APPROVED'
        transaction.save(update_fields=['status'])
        print("Pagamento aprovado!")

        return Response(
            {
                "order_id": transaction.order_id,
                "status": transaction.status,
                "amount": transaction.amount,
            },
            status=status.HTTP_200_OK,
        )


class PagamentoStatusView(APIView):
    def get(self, request, order_id: int):
        transaction = PaymentTransaction.objects.filter(order_id=order_id).first()
        if transaction is None:
            return Response(
                {"erro": "Pagamento nao encontrado para este pedido."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "order_id": transaction.order_id,
                "status": transaction.status,
                "amount": transaction.amount,
            },
            status=status.HTTP_200_OK,
        )
