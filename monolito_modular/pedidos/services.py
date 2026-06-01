from .models import Pedido
# Importamos APENAS das interfaces dos outros módulos!
from pagamento.services import PagamentoService
# Supondo que você crie um app/módulo separado para notificação
# from notificacao.services import NotificacaoService 

class PedidoService:
    @staticmethod
    def finalizar_pedido(pedido_id: int, valor_total: float):
        pedido = Pedido.objects.get(id=pedido_id)
        
        # 1. Chama o módulo de pagamento via interface
        sucesso = PagamentoService.processar_pagamento_mock(pedido_id, valor_total)
        
        if sucesso:
            pedido.status = 'PAGO'
            pedido.save()
            
            # 2. Chama a notificação (acoplamento via interface)
            # NotificacaoService.avisar_cozinha(pedido_id)
            pedido.status = 'COZINHA'
            pedido.save()
            
        return pedido