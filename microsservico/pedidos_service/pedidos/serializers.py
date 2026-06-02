from rest_framework import serializers

class CriarPedidoSerializer(serializers.Serializer):
    itens = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Lista de IDs dos itens do cardapio"
    )
    observacao = serializers.CharField(required=False, allow_blank=True)
