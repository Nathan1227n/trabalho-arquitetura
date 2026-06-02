from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CriarPedidoSerializer
from .models import Pedido, PedidoItem
from .services import PedidoService

from cardapio.services import CardapioService


class PedidoAPIView(APIView):
    def get(self, request):
        pedidos = PedidoService.listar_pedidos()
        resultado = []

        for pedido in pedidos:
            resultado.append({
                "pedido_id": pedido.id,
                "status": pedido.status,
                "criado_em": pedido.criado_em,
                "itens": [
                    {
                        "item_id": item.item_id,
                        "preco_congelado": item.preco_congelado,
                    }
                    for item in pedido.itens.all()
                ],
            })

        return Response(resultado, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CriarPedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        itens_ids = serializer.validated_data['itens']
        valor_total = 0
        itens_validados = []

        # 1. Validar itens comunicando-se com o módulo de Cardápio via Interface
        for item_id in itens_ids:
            item_data = CardapioService.obter_item(item_id)

            if not item_data or not item_data['disponivel']:
                return Response(
                    {"erro": f"Item {item_id} indisponível ou inexistente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            valor_total += float(item_data['preco'])
            itens_validados.append(item_data)

        # 2. Salvar o pedido no módulo local
        pedido = Pedido.objects.create(status='CRIADO')
        for item in itens_validados:
            PedidoItem.objects.create(
                pedido=pedido,
                item_id=item['id'],
                preco_congelado=item['preco'],
            )

        pedido_atualizado = PedidoService.finalizar_pedido(pedido.id, valor_total)

        return Response(
            {
                "mensagem": "Pedido processado e enviado para a cozinha!",
                "pedido_id": pedido_atualizado.id,
                "status_final": pedido_atualizado.status,
                "valor_total": valor_total,
            },
            status=status.HTTP_201_CREATED,
        )


class PedidoDetailAPIView(APIView):
    def patch(self, request, pedido_id: int):
        try:
            pedido = PedidoService.cancelar_pedido(pedido_id)
        except Pedido.DoesNotExist:
            return Response(
                {"erro": "Pedido não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as exc:
            return Response(
                {"erro": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "mensagem": "Pedido cancelado.",
                "pedido_id": pedido.id,
                "status": pedido.status,
            },
            status=status.HTTP_200_OK,
        )


class CancelarPedidoAPIView(PedidoDetailAPIView):
    pass
