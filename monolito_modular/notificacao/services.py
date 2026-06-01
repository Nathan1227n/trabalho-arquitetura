class NotificacaoService:
    @staticmethod
    def avisar_cozinha(pedido_id: int) -> bool:
        """
        Interface pública do módulo de notificação.
        No Monólito Modular, a chamada é direta, mas isolada nesta classe.
        """
        print(f"🔔 [MÓDULO NOTIFICAÇÃO]: Atenção Cozinha! O Pedido #{pedido_id} foi pago e já pode ser preparado.")
        return True