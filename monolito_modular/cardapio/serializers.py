from rest_framework import serializers
from .models import ItemCardapio

class ItemCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCardapio
        fields = ['id', 'nome', 'preco', 'disponivel']