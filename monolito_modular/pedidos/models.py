from django.db import models

# Create your models here.

class Pedido(models.Model):
    status = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pedidos_pedido'

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    item_id = models.IntegerField() # Referência "solta" ao Cardápio (Sem acoplamento)
    preco_congelado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'pedidos_item'
