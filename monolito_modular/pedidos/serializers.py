from rest_framework import serializers
from .models import Pedido # <-- Não esqueça de importar o modelo aqui

# Mantém o que você já tinha (Usado no POST)
class CriarPedidoSerializer(serializers.Serializer):
    itens = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Lista de IDs dos itens do cardápio"
    )

# Adiciona esse novo (Usado no GET)
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'status', 'criado_em']