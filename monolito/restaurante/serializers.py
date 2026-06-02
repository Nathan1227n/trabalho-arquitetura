from .models import ItemCardapio, Pedido, ItemPedido, Pagamento, Notificacao
from rest_framework import serializers

class ItemCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCardapio
        fields = '__all__'

class ItemPedidoDetailSerializer(serializers.ModelSerializer):
    """Serializer para ItemPedido aninhado dentro de Pedido"""
    class Meta:
        model = ItemPedido
        fields = ['id', 'item_cardapio', 'quantidade', 'preco']

class ItemPedidoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simples para ItemPedido (apenas para criação)"""
    class Meta:
        model = ItemPedido
        fields = ['item_cardapio', 'quantidade']

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'status', 'observacao']

class PedidoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhe do Pedido com itens aninhados"""
    itens = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = ['id', 'status', 'observacao', 'itens']
    
    def get_itens(self, obj):
        itens = ItemPedido.objects.filter(pedido=obj)
        return ItemPedidoDetailSerializer(itens, many=True).data

class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar Pedido com ItemPedido aninhados"""
    itens = ItemPedidoSimpleSerializer(many=True, write_only=True)
    
    class Meta:
        model = Pedido
        fields = ['itens', 'observacao']
    
    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        observacao = validated_data.pop('observacao')
        pedido = Pedido.objects.create(observacao=observacao)
        print(f"Pedido criado: {pedido.id}")
        
        for item_data in itens_data:
            item_cardapio = item_data['item_cardapio']
            quantidade = item_data['quantidade']
            
            ItemPedido.objects.create(
                pedido=pedido,
                item_cardapio=item_cardapio,
                preco=item_cardapio.preco,
                quantidade=quantidade
            )
        
        # Criar pagamento automaticamente
        Pagamento.objects.create(
            pedido=pedido,
            status='PENDENTE'
        )
        
        return pedido

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'
        
class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = '__all__'