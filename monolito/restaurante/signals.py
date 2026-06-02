from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pagamento, Notificacao, Pedido
import time

@receiver(post_save, sender=Pagamento)
def criar_notificacao_pagamento_aprovado(sender, instance, created, **kwargs):
    """
    Cria uma notificação e atualiza status do pedido quando um pagamento é aprovado
    """
    # Verifica se o status foi alterado para APROVADO
    if instance.status == 'APROVADO':
        print(f"Processando pagamento...")
        time.sleep(5)
        print(f"Pagamento feito!")
        
        # Atualiza o status do pedido para EM_PREPARACAO
        pedido = instance.pedido
        pedido.status = 'EM_PREPARACAO'
        pedido.save()
        
        # Verifica se já existe notificação para este pedido
        notificacao_existe = Notificacao.objects.filter(pedido=pedido).exists()
        
        if not notificacao_existe:
            notificacao = Notificacao.objects.create(pedido=pedido)
            print(f"Notificação criada para pedido: {notificacao.pedido.id}")
