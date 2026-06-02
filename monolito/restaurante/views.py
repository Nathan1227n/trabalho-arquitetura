from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ItemCardapio, ItemPedido, Pagamento, Pedido, Notificacao
from .serializers import (
    ItemCardapioSerializer, PedidoSerializer, PedidoDetailSerializer, PedidoCreateSerializer,
    ItemPedidoSerializer, PagamentoSerializer, NotificacaoSerializer
)

class CardapioViewSet(viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.filter(disponivel=True)
    serializer_class = ItemCardapioSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action == 'retrieve':
            return PedidoDetailSerializer
        return PedidoSerializer
    
    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """
        Cancela um pedido
        """
        pedido = self.get_object()
        
        # Verifica se o pedido já foi entregue ou cancelado
        if pedido.status in ['ENTREGUE', 'CANCELADO']:
            return Response(
                {'erro': f'Não é possível cancelar um pedido com status {pedido.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.status = 'CANCELADO'
        pedido.save()
        
        return Response(
            {
                'mensagem': 'Pedido cancelado com sucesso',
                'id': pedido.id,
                'status': pedido.status
            },
            status=status.HTTP_200_OK
        )
    
class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    lookup_field = 'pedido__id'
    lookup_url_kwarg = 'pedido_id'

class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer