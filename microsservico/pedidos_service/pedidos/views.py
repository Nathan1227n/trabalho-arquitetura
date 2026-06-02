from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Order, OrderItem
from .serializers import CriarPedidoSerializer
from . import clients

# App Celery usado apenas para PUBLICAR a task da cozinha na fila (RabbitMQ).
from core.celery import app as celery_app


class PedidoAPIView(APIView):
    def get(self, request):
        orders = Order.objects.prefetch_related('items').all()
        resultado = []

        for order in orders:
            resultado.append({
                "order_id": order.id,
                "status": order.status,
                "observacao": getattr(order, 'observacao', None),
                "created_at": order.created_at,
                "items": [
                    {
                        "item_id": item.item_id,
                        "frozen_price": item.frozen_price,
                    }
                    for item in order.items.all()
                ],
            })

        return Response(resultado, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CriarPedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        itens_ids = serializer.validated_data['itens']
        total = 0
        itens_validados = []

        # 1. Valida os itens chamando o servico de Cardapio via HTTP (timeout explicito)
        for item_id in itens_ids:
            try:
                item_data = clients.obter_item(item_id)
            except clients.ServiceUnavailable as exc:
                return Response(
                    {"erro": str(exc)},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            if not item_data or not item_data['available']:
                return Response(
                    {"erro": f"Item {item_id} indisponivel ou inexistente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total += float(item_data['price'])
            itens_validados.append(item_data)

        # 2. Salva o pedido no banco LOCAL do servico de pedidos
        order = Order.objects.create(status='CREATED', observacao=serializer.validated_data.get('observacao'))
        for item in itens_validados:
            OrderItem.objects.create(
                order=order,
                item_id=item['id'],
                frozen_price=item['price'],
            )

        # 3. Processa o pagamento via HTTP SINCRONO (timeout explicito)
        try:
            pagamento = clients.processar_pagamento(order.id, total)
        except clients.ServiceUnavailable as exc:
            # Degradacao controlada: o pedido fica como CREATED (sem pagamento).
            return Response(
                {
                    "erro": str(exc),
                    "order_id": order.id,
                    "status_final": order.status,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if pagamento.get('status') != 'APPROVED':
            return Response(
                {"erro": "Pagamento nao aprovado.", "order_id": order.id},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        order.status = 'PAID'
        order.save(update_fields=['status'])

        # 4. Notifica a cozinha via FILA ASSINCRONA (Celery + RabbitMQ).
        #    Se o servico de notificacao estiver fora do ar, a mensagem fica
        #    enfileirada no RabbitMQ e o pagamento NAO falha junto.
        try:
            celery_app.send_task(
                'notificacao.notificar_cozinha',
                args=[order.id, f"Pedido {order.id} pago. Enviar para a cozinha."],
            )
            order.status = 'KITCHEN'
            order.save(update_fields=['status'])
        except Exception as exc:
            print(f"Falha ao enfileirar notificacao do pedido {order.id}: {exc}")

        return Response(
            {
                "mensagem": "Pedido processado!",
                "order_id": order.id,
                "status_final": order.status,
                "total": total,
            },
            status=status.HTTP_201_CREATED,
        )


class PedidoDetailAPIView(APIView):
    def patch(self, request, order_id: int):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"erro": "Pedido nao encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status in ('PAID', 'KITCHEN'):
            return Response(
                {"erro": "Pedido ja foi pago ou enviado para a cozinha e nao pode ser cancelado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = 'CANCELLED'
        order.save(update_fields=['status'])

        return Response(
            {
                "mensagem": "Pedido cancelado.",
                "order_id": order.id,
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )


class CancelarPedidoAPIView(PedidoDetailAPIView):
    pass
