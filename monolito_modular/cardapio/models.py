from django.db import models

# Create your models here.

class ItemCardapio(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    disponivel = models.BooleanField(default=True)

    class Meta:
        db_table = 'cardapio_item' #Simula o Schema 'cardapio'
    