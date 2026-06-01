from rest_framework import viewsets
from .models import ItemCardapio
from .serializers import ItemCardapioSerializer

class ItemCardapioViewSet(viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer