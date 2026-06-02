from django.db import models

# Create your models here.

class Transacao(models.Model):
    #Referencia 'solta' ao pedido (sem chave estrangeira)
    pedido_id = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, default='PENDENTE')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pagamento_transacao'