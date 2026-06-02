# Versão 3 — Microsserviços (Sistema de Pedidos de Lanchonete)

Terceira versão do mesmo domínio (lanchonete) implementada como **microsserviços
independentes**, mantendo o mesmo stack das outras versões (Django 6.0.5 + Django
REST Framework + SQLite) e adicionando comunicação **HTTP síncrona** entre serviços
e **mensageria assíncrona** com **Celery + RabbitMQ**.

## Visão geral da arquitetura

Cada capacidade é um processo/container independente, com **banco de dados próprio e
isolado** (SQLite por serviço, em volume Docker separado). Não há banco compartilhado:
quando um serviço precisa de dado de outro, ele **chama a API** do outro.

| Serviço            | Porta (host) | Banco (volume)   | Responsabilidade                                   |
|--------------------|--------------|------------------|----------------------------------------------------|
| `cardapio`         | 8001         | `cardapio_db`    | CRUD de itens (nome, preço, disponibilidade)       |
| `pedidos`          | 8002         | `pedidos_db`     | Criar/listar/cancelar pedidos (**orquestrador**)   |
| `pagamento`        | 8003         | `pagamento_db`   | Processar pagamento (mock) e consultar status      |
| `notificacao`      | 8004         | `notificacao_db` | Health + listagem de notificações                  |
| `notificacao-worker` | —          | `notificacao_db` | **Worker Celery** que consome a fila e grava na tabela |
| `rabbitmq`         | 5672 / 15672 | —                | Broker da fila assíncrona (painel em 15672)        |

### Fluxo de um pedido (regra crítica: só vai para a cozinha após o pagamento)

```
Cliente
  │  POST /pedidos/  {"itens":[1,2]}
  ▼
┌──────────┐  GET  itens (HTTP, timeout)   ┌──────────┐
│ pedidos  │ ────────────────────────────► │ cardapio │
│          │  POST processar (HTTP, sync)  ┌──────────┐
│          │ ────────────────────────────► │pagamento │  (mock: sleep 5s → APPROVED)
│          │  publica task (Celery)        ┌──────────┐
│          │ ────────────────────────────► │ RabbitMQ │
└──────────┘                               └────┬─────┘
                                                │ consome (assíncrono)
                                                ▼
                                        ┌────────────────────┐
                                        │ notificacao-worker │ → grava tabela notifications
                                        └────────────────────┘
```

Estados do pedido: `CREATED → PAID → KITCHEN` (ou `CANCELLED`).

## Como rodar

Pré-requisito: Docker + Docker Compose.

```bash
cd microsservico
docker compose up --build
```

Sobe os 6 containers. Aguarde os health checks ficarem saudáveis (~20-30s).

Para parar:

```bash
docker compose down          # mantém os volumes (dados)
docker compose down -v       # remove também os bancos
```

## Endpoints principais

### Cardápio — http://localhost:8001
- `GET    /cardapio/itens/` — lista itens
- `POST   /cardapio/itens/` — cria item `{"name":"X-Burger","price":"25.00","available":true}`
- `GET    /cardapio/itens/<id>/` — detalhe
- `PUT/PATCH /cardapio/itens/<id>/` — atualiza
- `DELETE /cardapio/itens/<id>/` — remove
- `GET    /health/`

### Pedidos — http://localhost:8002
- `GET    /pedidos/` — lista pedidos
- `POST   /pedidos/` — cria pedido `{"itens":[1,2]}` (dispara pagamento + notificação)
- `PATCH  /pedidos/<id>/` — cancela (se ainda não pago)
- `GET    /health/`

### Pagamento — http://localhost:8003
- `POST   /pagamento/processar/` — `{"order_id":1,"amount":25.0}` (mock, sleep 5s)
- `GET    /pagamento/status/<order_id>/` — consulta status
- `GET    /health/`

### Notificação — http://localhost:8004
- `GET    /notificacao/` — lista as notificações gravadas (tabela `notifications`)
- `GET    /health/`

## Testando o fluxo completo

```bash
# 1) cria um item no cardápio
curl -X POST http://localhost:8001/cardapio/itens/ \
  -H "Content-Type: application/json" \
  -d '{"name":"X-Burger","price":"25.00","available":true}'

# 2) cria um pedido (leva ~5s por causa do mock de pagamento)
curl -X POST http://localhost:8002/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1]}'
# => {"mensagem":"Pedido processado!","order_id":1,"status_final":"KITCHEN","total":25.0}

# 3) confere o pagamento
curl http://localhost:8003/pagamento/status/1/
# => {"order_id":1,"status":"APPROVED","amount":"25.00"}

# 4) confere a notificação gravada pelo worker (via fila)
curl http://localhost:8004/notificacao/
# => [{"id":1,"order_id":1,"message":"Pedido 1 pago...","status":"SENT", ...}]
```

## Estratégia de resiliência

**Timeout explícito** em todas as chamadas HTTP entre serviços
([pedidos_service/pedidos/clients.py](pedidos_service/pedidos/clients.py)):

- Cardápio: `timeout=(3, 5)` (connect, read)
- Pagamento: `timeout=(3, 15)` (read maior por causa do `sleep(5)` do mock)

Se um serviço dependente não responde dentro do tempo, a chamada **falha rápido e de
forma controlada** (HTTP 503/502) em vez de travar o serviço de pedidos
indefinidamente.

## Experimentos obrigatórios (Seção 5 e 6 do trabalho)

### Derrubar o serviço de notificação e fazer um pedido
```bash
docker compose stop notificacao notificacao-worker
curl -X POST http://localhost:8002/pedidos/ -H "Content-Type: application/json" -d '{"itens":[1]}'
```
**Resultado:** o pedido é criado e o **pagamento é aprovado normalmente**
(`status_final` pode ficar em `KITCHEN` pois a mensagem foi *publicada* com sucesso no
RabbitMQ). A notificação **não é processada na hora** — fica enfileirada no broker.
Ao religar o worker, o backlog é consumido:
```bash
docker compose start notificacao-worker
curl http://localhost:8004/notificacao/   # a notificação atrasada aparece
```
**O pagamento NÃO falha junto com a notificação** — esse é o ganho do acoplamento
assíncrono via fila. (O painel do RabbitMQ em http://localhost:15672 — guest/guest —
mostra a mensagem aguardando na fila enquanto o worker está parado.)

### Simular falha no pagamento
Pare o serviço de pagamento (`docker compose stop pagamento`) e crie um pedido: o
serviço de pedidos retorna **502** por timeout/conexão, o pedido fica como `CREATED` e
os demais serviços (cardápio, notificação) continuam de pé. **Degradação parcial**, não
queda total.

### Rollback apenas do serviço de pagamento (sem afetar os outros)
Como cada serviço tem imagem, deploy e banco próprios, é possível voltar **só** o
pagamento para uma versão anterior sem tocar nos demais:
```bash
# reconstrói/recria apenas o container de pagamento
docker compose up -d --no-deps --build pagamento
# (ou, com uma imagem versionada anterior, troque a tag em docker-compose.yml e:)
docker compose up -d --no-deps pagamento
```
`--no-deps` garante que cardápio, pedidos e notificação **não** são reiniciados. O banco
do pagamento é um volume isolado, então o rollback do serviço não afeta os dados dos
outros.

### Adicionar campo "observação" em um pedido
Tocaria **apenas** o serviço de pedidos: `pedidos_service/pedidos/models.py` (campo
novo) + nova migration + `serializers.py`/`views.py`. Os outros 3 serviços não mudam,
pois não conhecem o schema interno de pedidos (comunicação só por API).

## Estrutura de diretórios

```
microsservico/
├── docker-compose.yml
├── cardapio_service/      # Django + DRF (CRUD do cardápio)
├── pedidos_service/       # Django + DRF + requests + celery (orquestrador)
│   └── pedidos/clients.py # chamadas HTTP com timeout
├── pagamento_service/     # Django + DRF (mock de pagamento)
└── notificacao_service/   # Django + DRF + celery (worker + tabela notifications)
    ├── core/celery.py
    └── notificacao/tasks.py
```

## Observações para o relatório comparativo

- **Mais difícil de implementar:** esta versão (microsserviços) — exige Docker Compose,
  broker de mensageria, comunicação HTTP e tratamento de falhas de rede.
- **Debug mais doloroso:** rastrear um pedido exige olhar logs de vários containers
  (`docker compose logs -f pedidos pagamento notificacao-worker`).
- **Maior vantagem:** isolamento real — escalar, derrubar, fazer deploy/rollback e
  trocar a implementação de um serviço sem afetar os outros; falha de um serviço degrada
  apenas parte do sistema.
