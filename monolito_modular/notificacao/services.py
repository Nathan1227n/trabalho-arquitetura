class NotificacaoService:
    @staticmethod
    def avisar_cozinha(pedido_id: int) -> bool:
        """Interface pública de notificação para a cozinha."""
        print(f"📣 Avisando a cozinha sobre o pedido {pedido_id}...")
        return True
