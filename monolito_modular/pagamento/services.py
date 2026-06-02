import time
from .models import Transacao


class PagamentoService:
    @staticmethod
    def processar_pagamento_mock(pedido_id: int, valor_total: float) -> str:
        """
        Salva a transação, simula lentidão e aprova.
        """
        print(f"�� Iniciando pagamento do pedido {pedido_id}...")

        transacao, created = Transacao.objects.get_or_create(
            pedido_id=pedido_id,
            defaults={
                'valor': valor_total,
                'status': 'PROCESSANDO',
            },
        )
        if not created:
            transacao.valor = valor_total
            transacao.status = 'PROCESSANDO'
            transacao.save(update_fields=['valor', 'status'])

        # Simula a lentidão (Experimento Obrigatório)
        time.sleep(5)

        transacao.status = 'APROVADO'
        transacao.save(update_fields=['status'])
        print("✅ Pagamento aprovado!")

        return transacao.status

    @staticmethod
    def consultar_status(pedido_id: int):
        transacao = Transacao.objects.filter(pedido_id=pedido_id).first()
        if transacao is None:
            return None
        return transacao.status
