import time

class PagamentoService:
    @staticmethod
    def processar_pagamento_mock(pedido_id: int, valor_total: float) -> bool:
        """
        Interface pública do pagamento.
        Cumpre o Experimento Obrigatório (sleep 5s).
        """
        print(f"💸 Iniciando pagamento do pedido {pedido_id}...")
        
        # Simula a lentidão
        time.sleep(5)
        
        print("✅ Pagamento aprovado!")
        return True