from .models import Pedido
# Importamos APENAS das interfaces dos outros módulos!
from pagamento.services import PagamentoService
from notificacao.services import NotificacaoService


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
            if NotificacaoService.avisar_cozinha(pedido_id):
                pedido.status = 'COZINHA'
                pedido.save()

        return pedido

    @staticmethod
    def listar_pedidos():
        return Pedido.objects.prefetch_related('itens').all()

    @staticmethod
    def cancelar_pedido(pedido_id: int):
        pedido = Pedido.objects.get(id=pedido_id)
        if pedido.status == 'COZINHA':
            raise ValueError('Pedido já foi para cozinha e não pode ser cancelado.')

        pedido.status = 'CANCELADO'
        pedido.save()
        return pedido