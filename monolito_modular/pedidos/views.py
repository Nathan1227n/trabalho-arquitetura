from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Adicionamos a importação do PedidoSerializer aqui
from .serializers import CriarPedidoSerializer, PedidoSerializer 
from .models import Pedido, PedidoItem
from .services import PedidoService

# Importação da interface do OUTRO módulo (Padrão Modular)
from cardapio.services import CardapioService 

class PedidoAPIView(APIView):
    # --- NOVO: Método para listar os pedidos ---
    def get(self, request):
        """Lista todos os pedidos"""
        pedidos = Pedido.objects.all()
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)
    # -------------------------------------------

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
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            valor_total += float(item_data['preco'])
            itens_validados.append(item_data)

        # 2. Salvar o pedido no módulo local
        pedido = Pedido.objects.create(status='CRIADO')
        for item in itens_validados:
            PedidoItem.objects.create(
                pedido=pedido,
                item_id=item['id'],
                preco_congelado=item['preco']
            )

        pedido_atualizado = PedidoService.finalizar_pedido(pedido.id, valor_total)

        return Response({
            "mensagem": "Pedido processado e enviado para a cozinha!",
            "pedido_id": pedido_atualizado.id,
            "status_final": pedido_atualizado.status,
            "valor_total": valor_total
        }, status=status.HTTP_201_CREATED)


class CancelarPedidoAPIView(APIView):
    def patch(self, request, pedido_id):
        """Cancela um pedido específico"""
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Regra: Só pode cancelar se ainda não foi para a cozinha
            if pedido.status in ['COZINHA', 'PAGO']:
                return Response(
                    {"erro": "Não é possível cancelar um pedido que já foi pago ou está na cozinha."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            pedido.status = 'CANCELADO'
            pedido.save()
            return Response({"mensagem": f"Pedido {pedido_id} cancelado com sucesso."})
            
        except Pedido.DoesNotExist:
            return Response({"erro": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)