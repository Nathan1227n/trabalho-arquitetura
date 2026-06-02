# Versão 2 — Monolito Modular (Sistema de Pedidos de Lanchonete)

Segunda versão do domínio de lanchonete implementada como um **monolito com separação
modular explícita**, mantendo o mesmo stack das outras versões (Django 6.0.5 + Django
REST Framework + SQLite) mas com **cada módulo expondo uma interface pública clara**
(`Service`) e **nenhum acesso direto entre repositórios de módulos diferentes**.

## Visão geral da arquitetura

Uma única aplicação Django com um banco SQLite, mas os 4 módulos (cardápio, pedidos,
pagamento, notificação) são **organizados como domínios isolados**. A comunicação entre
eles é feita **exclusivamente via interfaces de serviço**, não via acesso direto a models
ou repositórios.

| Aspecto               | Detalhes                                                          |
|-----------------------|-------------------------------------------------------------------|
| Processo              | Um único Django (porta 8000)                                      |
| Banco de dados        | Um único SQLite (`db.sqlite3`), mas com prefixos de tabela        |
| Módulos               | cardápio, pedidos, pagamento, notificação (cada um isolado)       |
| Comunicação           | Via interfaces de serviço tipadas (`CardapioService`, etc.)       |
| Acesso a dados        | Cada módulo tem seus próprios models (não acessa models de outro) |
| Escalabilidade        | Ainda limitado ao vertical scale, mas com melhor separação        |

### Fluxo de um pedido (via interfaces de serviço)

```
Cliente
  │  POST /pedidos/
  ▼
┌────────────────────────────────────────────────────────────┐
│             Processo Django (único)                        │
│                                                             │
│  ┌──────────────┐                                          │
│  │  PedidosView │ (ViewSet)                                │
│  │      ↓       │                                          │
│  │ PedidoService│ (interface pública)                      │
│  │      │       │                                          │
│  │      ├─→ CardapioService.validar_itens()               │
│  │      │                                                  │
│  │      ├─→ PagamentoService.processar() [sleep 5s]      │
│  │      │                                                  │
│  │      └─→ NotificacaoService.notificar()               │
│  └──────────────┘                                          │
└────────────────────────────────────────────────────────────┘
```

**Ponto-chave:** `PedidoService` não acessa diretamente `models.Pagamento` ou
`models.Cardapio` — chama apenas as interfaces públicas dos outros módulos.


## Como rodar

Pré-requisito: Python 3.10+, pip.

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Ativar ambiente virtual

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar migrações

```bash
python manage.py migrate
```

### 5. Criar dados de teste (itens do cardápio)

```bash
python manage.py shell
```

Dentro do shell:
```python
from cardapio.models import ItemCardapio

ItemCardapio.objects.create(nome="X-Burger", preco=25.00, disponivel=True)
ItemCardapio.objects.create(nome="Refrigerante", preco=8.00, disponivel=True)
ItemCardapio.objects.create(nome="Bolo", preco=15.00, disponivel=True)

exit()
```

### 6. Iniciar servidor Django

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`.

### Acessar a documentação da API

- Swagger: `http://localhost:8000/api/docs/`
- Admin Django: `http://localhost:8000/admin/`

## Endpoints principais

### Cardápio — http://localhost:8000/cardapio/
- `GET    /cardapio/itens/` — lista itens
- `POST   /cardapio/itens/` — cria item `{"nome":"X-Burger","preco":"25.00","disponivel":true}`
- `GET    /cardapio/itens/<id>/` — detalhe
- `PUT/PATCH /cardapio/itens/<id>/` — atualiza
- `DELETE /cardapio/itens/<id>/` — remove

### Pedidos — http://localhost:8000/pedidos/
- `GET    /pedidos/` — lista pedidos
- `POST   /pedidos/` — cria pedido `{"itens":[1,2],"observacao":"sem cebola"}`
- `GET    /pedidos/<id>/` — detalhe
- `PATCH  /pedidos/<id>/` — atualiza
- `DELETE /pedidos/<id>/` — cancela

### Pagamento — http://localhost:8000/pagamento/
- `GET    /pagamento/status/<pedido_id>/` — consulta status do pagamento

### Notificação — http://localhost:8000/notificacao/
- `GET    /notificacao/` — lista notificações

## Testando o fluxo completo

```bash
# 1) criar item no cardápio
curl -X POST http://localhost:8000/cardapio/itens/ \
  -H "Content-Type: application/json" \
  -d '{"nome":"X-Burger","preco":"25.00","disponivel":true}'

# 2) criar um pedido (leva ~5s por causa do sleep do pagamento)
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1],"observacao":""}'

# 3) listar pedidos
curl http://localhost:8000/pedidos/

# 4) consultar status de pagamento
curl http://localhost:8000/pagamento/status/1/

# 5) listar notificações
curl http://localhost:8000/notificacao/
```

## Arquitetura de Módulos

### Cada módulo expõe uma interface pública (`Service`)

**Exemplo: `cardapio/services.py`**
```python
class CardapioService:
    @staticmethod
    def validar_itens(item_ids):
        # Retorna lista de itens ou levanta exceção
        pass

    @staticmethod
    def obter_preco_total(item_ids):
        # Retorna preço total
        pass
```

**Uso em outro módulo (`pedidos/services.py`)**
```python
class PedidoService:
    def criar_pedido(self, item_ids):
        # Chama APENAS a interface pública do cardápio
        itens = CardapioService.validar_itens(item_ids)
        preco = CardapioService.obter_preco_total(item_ids)
        # ... resto da lógica
```

### Nenhum módulo acessa diretamente models de outro

```

## Problema de isolamento de dados (ainda no monolito)

Apesar da separação de interfaces, **todas as tabelas estão no mesmo banco SQLite**. Isto
significa:

1. **Não há verdadeira isolação de schema** — apenas prefixos de tabela (`pedido_*`,
   `pagamento_*`, `cardapio_*`). Um erro de SQL em um módulo ainda pode afetar o banco
   inteiro.
2. **Não há escalabilidade real** — o banco é um bottleneck único. Se cardápio recebe
   10x mais carga, todo o banco sofre.
3. **Transactions distribuídas não existem** — se o pagamento falha após validar itens,
   a mudança de estado em pedidos já ocorreu.

## Experimentos obrigatórios 

### Trocar a implementação do módulo de pagamento sem afetar outros

**Cenário:** Você quer mudar de um mock com `sleep(5)` para uma integração real com
uma API de pagamento externa (ex: Stripe, PayPal).

#### Passo 1: Edite apenas `pagamento/services.py`

```python
# ANTES (mock com sleep)
class PagamentoService:
    @staticmethod
    def processar_pagamento(pedido_id, valor):
        sleep(5)  # simulação
        return {"status": "APPROVED", "order_id": pedido_id}

# DEPOIS (chamada real a Stripe)
import stripe

class PagamentoService:
    @staticmethod
    def processar_pagamento(pedido_id, valor):
        try:
            response = stripe.PaymentIntent.create(
                amount=int(valor * 100),  # em centavos
                currency="brl",
            )
            return {
                "status": "APPROVED" if response.status == "succeeded" else "REJECTED",
                "order_id": pedido_id,
                "transaction_id": response.id
            }
        except stripe.error.StripeError as e:
            return {"status": "REJECTED", "error": str(e)}
```

#### Resultado esperado

- **Nenhuma mudança necessária** em `pedidos/`, `cardapio/` ou `notificacao/`.
- Os outros módulos continuam chamando `PagamentoService.processar_pagamento()` — a
  assinatura pública não mudou.
- O fluxo de criação de pedidos funciona com Stripe sem tocar em nenhum outro módulo.

**Tempo estimado:** ~5-10 minutos (apenas editar um arquivo, `pagamento/services.py`).

**Resultado:** Ao criar um pedido, a requisição inteira **leva 5 segundos**. Durante esse
tempo:
- Outros usuários tentando acessar `/cardapio/itens/` também **travam** — o servidor
  Django inteiro está processando pagamento.
- Sem isolamento real, o banco também sofre lock de escrita.

**Diferença vs. monolito simples:**
- No **monolito simples**, não há separação nem de interface — é pior.
- No **monolito modular**, a falha está bem documentada (interface clara), mas o
  impacto é o mesmo (tudo trava).
- Em **microsserviços**, o serviço de cardápio continua respondendo rápido — pagamento
  fica lento em seu container próprio.

## Documentação para o relatório comparativo

### Qual é o ganho do monolito modular vs. monolito simples?

1. **Clareza arquitetural:** Interfaces públicas deixam explícito quem depende de quem.
2. **Facilidade de evolução:** Trocar implementação de um módulo sem risco de quebrar
   outros (desde que você não mude a assinatura pública).
3. **Pré-caminho para microsserviços:** Se amanhã você quiser separar pagamento em um
   serviço próprio, a interface já existe — você só precisa mover o código para outro
   container.

### Qual é a limitação principal?

**Tudo ainda compartilha o mesmo processo e banco.** Não há isolamento real de:
- **CPU:** Um módulo lento trava todo o servidor.
- **Banco:** Todas as tabelas no mesmo SQLite, sem schemas separados.
- **Deployment:** Você não pode fazer deploy de apenas um módulo sem religar todo o
  servidor.

### Quais módulos poderiam virar serviços independentes amanhã?

**Todos os 4 poderiam**, desde que:

1. **Cardápio:** é puro CRUD, sem dependências.
2. **Pagamento:** atualmente não depende de ninguém (apenas recebe pedido_id e valor).
   Pode virar serviço isolado imediatamente.
3. **Notificação:** atualmente chamada sincronamente após pagamento. Para virar serviço,
   precisaria de uma **fila assíncrona** (RabbitMQ/Redis) para publicar eventos de
   pedidos pagos.
4. **Pedidos:** é o orquestrador — precisa de chamadas HTTP/RPC para cardápio e
   pagamento. Funciona bem como microsserviço.

**Esforço para migrar para microsserviços:**

- **Código:** Já está 80% pronto — interfaces públicas existem, não há acoplamento de
  modelos.
- **Infraestrutura:** Precisa de Docker + Docker Compose, broker de mensageria
  (RabbitMQ), comunicação HTTP com timeouts.
- **Testes:** Precisaria de testes de integração entre serviços (teste de timeout,
  falha de conexão, etc.).

## Estrutura de diretórios

```
monolito_modular/
├── core/                  # Configurações do Django
│   ├── settings.py       # Settings principais
│   ├── urls.py          # Rotas principais
│   ├── asgi.py          # ASGI
│   └── wsgi.py          # WSGI
├── cardapio/             # Módulo isolado de cardápio
│   ├── models.py        # Models (ItemCardapio)
│   ├── serializers.py   # Serializers DRF
│   ├── services.py      # Interface pública (CardapioService)
│   ├── views.py         # ViewSets
│   ├── urls.py          # Rotas
│   ├── admin.py         # Admin Django
│   ├── apps.py          # Config da app
│   ├── tests.py         # Testes
│   └── migrations/      # Migrações
├── pedidos/              # Módulo isolado de pedidos
│   ├── models.py        # Models (Pedido, ItemPedido)
│   ├── serializers.py   # Serializers
│   ├── services.py      # Interface pública (PedidoService)
│   ├── views.py         # ViewSets
│   ├── urls.py          # Rotas
│   ├── tests.py         # Testes
│   └── migrations/      # Migrações
├── pagamento/            # Módulo isolado de pagamento
│   ├── models.py        # Models (Pagamento)
│   ├── serializers.py   # Serializers
│   ├── services.py      # Interface pública (PagamentoService)
│   ├── views.py         # ViewSets
│   ├── urls.py          # Rotas
│   ├── tests.py         # Testes
│   └── migrations/      # Migrações
├── notificacao/          # Módulo isolado de notificação
│   ├── models.py        # Models (Notificacao)
│   ├── serializers.py   # Serializers
│   ├── services.py      # Interface pública (NotificacaoService)
│   ├── views.py         # ViewSets
│   ├── urls.py          # Rotas
│   ├── tests.py         # Testes
│   └── migrations/      # Migrações
├── manage.py
├── db.sqlite3           # Banco único (SQLite)
├── requirements.txt     # Dependências
└── README.md
```

## Observações para o relatório comparativo

- **Mais fácil que microsserviços:** não exige Docker, broker de mensageria ou
  tratamento complexo de falhas de rede.
- **Mais estruturado que monolito simples:** interfaces públicas deixam claro quem
  depende de quem, facilitando evolução.
- **Ainda com limitações reais:** isolamento de dados/CPU/deployment não existe —
  tudo compartilha o mesmo processo e banco.
- **Pré-caminho ideal:** se você quer migrar de monolito para microsserviços, começar
  com monolito modular reduz o risco — a maior parte da arquitetura de separação já
  está pronta.
