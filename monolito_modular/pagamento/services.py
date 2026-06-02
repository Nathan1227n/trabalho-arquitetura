import time


class PagamentoService:
    _status = {}

    @staticmethod
    def processar_pagamento_mock(pedido_id: int, valor_total: float) -> bool:
        """
        Interface pública do pagamento.
        Cumpre o Experimento Obrigatório (sleep 5s).
        """
        print(f"💸 Iniciando pagamento do pedido {pedido_id}...")

        # Simula a lentidão
        time.sleep(5)

        PagamentoService._status[pedido_id] = 'PAGO'
        print("✅ Pagamento aprovado!")
        return True

    @staticmethod
    def consultar_status(pedido_id: int):
        return PagamentoService._status.get(pedido_id)
