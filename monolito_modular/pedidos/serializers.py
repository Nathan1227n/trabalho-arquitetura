from rest_framework import serializers
from .models import Pedido 

class CriarPedidoSerializer(serializers.Serializer):
    itens = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Lista de IDs dos itens do cardápio"
    )

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'status', 'criado_em']