from django.db import models
import uuid

class ItemCardapio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome
    
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('CANCELADO', 'Cancelado'),
        ('PENDENTE', 'Pendente'),
        ('EM_PREPARACAO', 'Em Preparação'),
        ('PRONTO', 'Pronto'),
        ('ENTREGUE', 'Entregue'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - Status: {self.status}"

class ItemPedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    item_cardapio = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    
    def __str__(self):
        return f"Item do pedido #{self.pedido.id} - Item do cardápio #{self.item_cardapio.id}"

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    def __str__(self):
        return f"Pagamento do pedido #{self.pedido.id} - Status: {self.status}"
    
class Notificacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"O pedido #{self.pedido.id} foi pago."