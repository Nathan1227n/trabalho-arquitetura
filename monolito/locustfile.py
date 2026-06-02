from locust import HttpUser, task
import random

class TesteCargaPedidos(HttpUser):
    
    # comando para rodar o teste com interface: python -m locust -f locustfile.py --host=http://localhost:8000 
    # o teste roda na porta 8089
    
    @task
    def criar_pedido(self):
        payload = {
            "itens": [
                {
                    "item_cardapio": "2",
                    "quantidade": random.randint(1, 3)
                }
            ],
            "observacao": f"Teste Locust #{random.randint(1, 10000)}"
        }
        self.client.post(
            "/api/pedidos/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )