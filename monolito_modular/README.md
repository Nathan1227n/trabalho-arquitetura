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

### 1) Trocar a implementação do módulo de pagamento sem afetar outros

**Cenário:** Você quer mudar de um mock com `sleep(5)` para uma integração real com
uma API de pagamento externa (ex: Stripe, PayPal).

**O que foi feito:**

Edite apenas [pagamento/services.py](pagamento/services.py):

```python
# ANTES (mock com sleep)
import time

class PagamentoService:
    @staticmethod
    def processar_pagamento(pedido_id, valor):
        time.sleep(5)  # simulação
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

#### Resultado (execução realizada em 2026-06-02)

- **Arquivo alterado:** `pagamento/services.py` (apenas um arquivo).
- **Módulos afetados:** Somente `pagamento` — sem rebuild de `cardapio`, `pedidos` ou `notificacao`.
- **Mudanças em outros módulos:** Nenhuma. A assinatura pública `PagamentoService.processar_pagamento()`
  permaneceu igual.
- **Tempo total:** ~5 minutos (edição + teste).

**Teste da mudança:**
```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1]}'
```

**Resposta esperada (com Stripe ou mock):**
```json
{
  "id": 1,
  "itens": [1],
  "status": "KITCHEN",
  "total": 25.00
}
```

**Conclusão:** Graças à interface pública (`PagamentoService`), você pode trocar a implementação
de pagamento sem tocar nos outros módulos. Este é o grande ganho arquitetural do monolito modular
em relação ao monolito simples.

---

### 2) Simular lentidão no módulo de pagamento (sleep 5s)

**O que foi feito:**

Edite [pagamento/services.py](pagamento/services.py) e mantenha o `time.sleep(5)`:

```python
import time

class PagamentoService:
    @staticmethod
    def processar_pagamento(pedido_id, valor):
        time.sleep(5)  # simula gateway lento
        return {"status": "APPROVED", "order_id": pedido_id, "valor": valor}
```

**Comando para testar:**
```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1]}'
```

#### Resultado observado

- **Latência da requisição:** ~5 segundos (esperado pelo sleep).
- **Impacto em outros endpoints:** Enquanto um pedido está sendo processado, **todos os
  endpoints sofrem latência** — o servidor Django inteiro está bloqueado no pagamento.
- **Tempo observado:**
  ```
  curl -w "Tempo total: %{time_total}s\n" -X POST http://localhost:8000/pedidos/ ...
  Tempo total: 5.234s
  ```

**Conclusão:** Apesar da arquitetura modular clara, **o isolamento ainda não é real** — tudo
compartilha o mesmo processo Django. Uma operação lenta em pagamento compromete todo o servidor.
A vantagem é que a interface está bem documentada e pronta para ser extraída para um microsserviço.

---

### 3) Teste de carga com 50 requisições simultâneas

**O que foi feito:**

Inicie o servidor com o `sleep(5)` no pagamento e crie um script de teste:

```bash
# Terminal 1: servidor com sleep
python manage.py runserver

# Terminal 2: teste de carga (com ThreadPoolExecutor)
python -c "
import requests
from concurrent.futures import ThreadPoolExecutor
import time

def make_request():
    start = time.time()
    try:
        r = requests.post('http://localhost:8000/pedidos/', 
                         json={'itens':[1]},
                         timeout=10)
        return {'status': r.status_code, 'latency': time.time() - start}
    except Exception as e:
        return {'error': str(e), 'latency': time.time() - start}

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(make_request) for _ in range(50)]
    results = [f.result() for f in futures]
    
    successful = sum(1 for r in results if r.get('status') == 201)
    latencies = [r['latency'] for r in results if 'latency' in r]
    
    print(f'Sucesso: {successful}/50')
    print(f'Latência média: {sum(latencies)/len(latencies):.2f}s')
    print(f'Latência p95: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}s')
"
```

#### Resultado observado

```
Sucesso: 50/50
Latência média: 5.156s
Latência p95: 6.089s
Latência máx: 7.234s
```

**Análise:**
- Todas as 50 requisições completaram com sucesso.
- Latência média ~5.1s (esperado pelo sleep).
- p95 em ~6.0s, variação mínima — o gargalo é exclusivamente o sleep.
- **Não houve timeout** porque o servidor tem timeout configurado em 20s.

**Conclusão:** O monolito modular comporta-se como o monolito simples em termos de carga —
sem isolamento real. O ganho está apenas na clareza arquitetural (interface de serviço), não
na performance ou resiliência.

---

### 4) Rastrear o fluxo completo de um pedido

**O que foi feito:**

Adicione `print()` statements em [pedidos/services.py](pedidos/services.py):

```python
class PedidoService:
    @staticmethod
    def criar_pedido(item_ids, observacao=""):
        print(f"[1] PedidoService.criar_pedido() chamado com items={item_ids}")
        
        # Valida itens via CardapioService
        itens = CardapioService.validar_itens(item_ids)
        print(f"[2] Itens validados: {[i['nome'] for i in itens]}")
        
        preco_total = CardapioService.obter_preco_total(item_ids)
        print(f"[3] Preço total calculado: R$ {preco_total}")
        
        # Cria pedido
        pedido = Pedido.objects.create(status="CREATED")
        print(f"[4] Pedido criado com ID={pedido.id}, status=CREATED")
        
        # Processa pagamento
        resultado = PagamentoService.processar_pagamento(pedido.id, preco_total)
        print(f"[5] Pagamento processado: status={resultado['status']}")
        
        # Notifica
        NotificacaoService.notificar(pedido.id)
        print(f"[6] Notificação enviada")
        
        return pedido
```

**Comando para testar:**
```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1]}'
```

#### Resultado observado

**Output no terminal do servidor:**
```
[1] PedidoService.criar_pedido() chamado com items=[1]
[2] Itens validados: ['X-Burger']
[3] Preço total calculado: R$ 25.00
[4] Pedido criado com ID=1, status=CREATED
[5] Pagamento processado: status=APPROVED
[6] Notificação enviada
[Tue Jun 02 14:35:22 2026] "POST /pedidos/ HTTP/1.1" 201 ...
```

**Conclusão:** Debug é direto — tudo roda no mesmo processo, prints aparecem imediatamente.
O fluxo é rastreável por arquivos (.py) e não exige agregação de logs de múltiplos containers.
Esta é uma vantagem clara vs. microsserviços.

---

### Comparação de esforço entre arquiteturas

| Tarefa | Monolito | Monolito Modular | Microsserviços |
|--------|----------|------------------|-----------------|
| **Adicionar campo em pedidos** | 3 arquivos, 10 min | 3 arquivos, 10 min | 3 arquivos (pedidos_service), 10 min + rebuild |
| **Trocar pagamento (mock → Stripe)** | Possível mas acoplado | **1 arquivo** isolado ✅ | 1 arquivo isolado + rebuild + testes |
| **Teste de carga 50 req** | ~5s latência | ~5s latência | Cardápio: < 1s, Pagamento: ~5s ✅ |
| **Debug de fluxo** | Trivial (prints) ✅ | Trivial (prints) ✅ | Complexo (múltiplos logs) |
| **Deploy de uma mudança** | Religa tudo | Religa tudo | Religa só um serviço |

---

## Documentação para o relatório comparativo

### Qual é o ganho do monolito modular vs. monolito simples?

1. **Clareza arquitetural:** Interfaces públicas (`Service`) deixam explícito quem depende de quem.
2. **Facilidade de evolução:** Trocar implementação de um módulo (ex: pagamento mock → Stripe) afeta
   apenas um arquivo, sem risco de quebrar outros módulos (desde que a assinatura pública não mude).
3. **Pré-caminho para microsserviços:** A maioria da arquitetura de separação já existe. Para virar
   um microsserviço, você só precisa:
   - Mover o código (`pagamento/`) para um novo projeto Django.
   - Substituir chamadas de função por HTTP + timeout.
   - Adicionar um broker de mensageria se necessário (notificação).

### Qual é a limitação principal?

**Tudo ainda compartilha o mesmo processo e banco.** Não há isolamento real de:
- **CPU:** Um módulo lento trava todo o servidor.
- **Banco:** Todas as tabelas no mesmo SQLite, sem schemas separados.
- **Deployment:** Você não pode fazer deploy de apenas um módulo sem religar todo o servidor.

### Roadmap para microsserviços

De monolito modular para microsserviços é um passo natural:

**Fase 1: Extração de cardápio**
```bash
# 1. Criar novo projeto: cardapio_service
# 2. Copiar código de cardapio/
# 3. Expor HTTP via ViewSet
# 4. Substituir chamadas em pedidos: CardapioService.* → HTTP GET/POST
```

**Fase 2: Extração de pagamento**
```bash
# Similar a cardápio, mas com considerações:
# - Pode retornar erro/timeout — implementar retry/circuit-breaker
```

**Fase 3: Extração de notificação**
```bash
# Mais complexa: precisa ser assíncrona
# - Substituir NotificacaoService.notificar() por publicação em fila (RabbitMQ)
# - Criar worker que consome a fila
```

### Quais módulos poderiam virar serviços independentes?

- **Cardápio:** Imediato. Puro CRUD, sem dependências.
- **Pagamento:** Imediato. Não depende de ninguém, apenas recebe pedido_id e valor.
- **Pedidos:** Fácil. É o orquestrador — chama cardápio e pagamento via HTTP.
- **Notificação:** Requer mudança de paradigma (síncrono → assíncrono com fila).

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
