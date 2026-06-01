from .models import Pedido
# Importamos APENAS da interface do módulo de pagamento (Padrão Modular)
from pagamento.services import PagamentoService
from notificacao.services import NotificacaoService

class PedidoService:
    @staticmethod
    def finalizar_pedido(pedido_id: int, valor_total: float):
        pedido = Pedido.objects.get(id=pedido_id)
        
        # 1. Chama o módulo de pagamento via interface
        # Aqui recebemos o status ('APROVADO', 'PENDENTE', etc)
        status_pagamento = PagamentoService.processar_pagamento_mock(pedido_id, valor_total)
        
        # Se for aprovado, atualizamos o pedido
        if status_pagamento == 'APROVADO':
            pedido.status = 'PAGO'
            pedido.save()
            
            # 2. Chama a notificação (acoplamento via interface)
            NotificacaoService.avisar_cozinha(pedido.id)

            pedido.status = 'COZINHA'
            pedido.save()
            
        return pedido