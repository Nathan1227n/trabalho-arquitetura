from .models import ItemCardapio

class CardapioService:
    @staticmethod
    def obter_item(item_id: int):
        try:
            item = ItemCardapio.objects.get(id=item_id)
            return {
                "id": item.id,
                "nome": item.nome,
                "preco": item.preco,
                "disponivel": item.disponivel
            }
        except ItemCardapio.DoesNotExist:
            return None