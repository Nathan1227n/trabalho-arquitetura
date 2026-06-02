from django.contrib import admin
from .models import ItemCardapio, Pedido, ItemPedido, Pagamento, Notificacao

@admin.register(ItemCardapio)
class ItemCardapioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'disponivel')
    list_filter = ('disponivel',)
    search_fields = ('nome',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'observacao')
    list_filter = ('status',)
    search_fields = ('id',)

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'item_cardapio', 'quantidade', 'preco')
    list_filter = ('pedido',)
    search_fields = ('pedido__id',)

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status')
    list_filter = ('status',)
    search_fields = ('pedido__id',)

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido')
    search_fields = ('pedido__id',)
