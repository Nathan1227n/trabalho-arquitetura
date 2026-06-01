import time
from .models import Transacao

class PagamentoService:
    @staticmethod
    def processar_pagamento_mock(pedido_id: int, valor_total: float) -> str:
        """
        Salva a transação, simula lentidão e aprova.
        """
        print(f"💸 Iniciando pagamento do pedido {pedido_id}...")
        
        # Registra a transação no banco isolado
        transacao = Transacao.objects.create(
            pedido_id=pedido_id,
            valor=valor_total,
            status='PROCESSANDO'
        )
        
        # 🛑 Simula a lentidão (Experimento Obrigatório)
        time.sleep(5)
        
        # Aprova o pagamento
        transacao.status = 'APROVADO'
        transacao.save()
        print("✅ Pagamento aprovado!")
        
        return transacao.status