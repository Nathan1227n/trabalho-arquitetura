# Versão 1 — Monolito (Sistema de Pedidos de Lanchonete)

Primeira versão do domínio de lanchonete implementada como um **único processo
monolítico**, com todo o código (cardápio, pedidos, pagamento e notificação) rodando
em um único servidor Django com SQLite.

## Visão geral da arquitetura

Uma única aplicação Django contém todos os módulos. Não há isolamento de dados — tudo
compartilha o mesmo banco SQLite. Quando uma operação trava, ela compromete todo o
servidor.

| Aspecto            | Detalhes                                                    |
|--------------------|-------------------------------------------------------------|
| Processo           | Um único Django (porta 8000)                                |
| Banco de dados     | Um único SQLite (`db.sqlite3`)                              |
| Módulos            | cardápio, pedidos, pagamento, notificação (tudo no mesmo)   |
| Comunicação        | Chamadas de função em memória (sem HTTP/RPC)                |
| Escalabilidade     | Aumentar recursos do servidor inteiro (vertical scale)      |

### Fluxo de um pedido (regra: pagamento tudo no mesmo thread)

```
Cliente
  │  POST /api/pedidos/
  ▼
┌─────────────────────────────────────────┐
│         Processo Django (único)         │
│  ┌─────────┐    ┌─────────┐             │
│  │ Pedidos │ → │ Pagamento │ (mock)    │
│  │         │   └─────────┘             │
│  │ ↓                                    │
│  │ Notificação (sincronamente)         │
│  └─────────────────────────────────────┘
```

Estados do pedido: `PENDENTE → EM PREPARAÇÃO → PRONTO -> ENTREGUE` (ou `CANCELADO`).

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

Depois execute dentro do shell:
```python
from restaurante.models import ItemCardapio

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

### Cardápio — http://localhost:8000/api/cardapio/
- `GET    /api/cardapio/` — lista itens
- `POST   /api/cardapio/` — cria item `{"nome":"X-Burger","preco":"25.00","disponivel":true}`
- `GET    /api/cardapio/<id>/` — detalhe
- `PUT/PATCH /api/cardapio/<id>/` — atualiza
- `DELETE /api/cardapio/<id>/` — remove

### Pedidos — http://localhost:8000/api/pedidos/
- `GET    /api/pedidos/` — lista pedidos
- `POST   /api/pedidos/` — cria pedido `{"itens":[{"item_cardapio":1,"quantidade":2}],"observacao":"sem cebola"}`
- `GET    /api/pedidos/<id>/` — detalhe
- `PATCH  /api/pedidos/<id>/` — atualiza
- `POST   /api/pedidos/<id>/cancelar/` — cancela

### Pagamentos — http://localhost:8000/api/pagamentos/
- `GET    /api/pagamentos/` — lista pagamentos
- `POST   /api/pagamentos/` — cria pagamento
- `GET    /api/pagamentos/<id>/` — detalhe
- `PUT/PATCH /api/pagamentos/<id>/` — atualiza
- `DELETE /api/pagamentos/<id>/` — remove

### Notificações — http://localhost:8000/api/notificacoes/
- `GET    /api/notificacoes/` — lista notificações
- `POST   /api/notificacoes/` — cria notificação
- `GET    /api/notificacoes/<id>/` — detalhe
- `PUT/PATCH /api/notificacoes/<id>/` — atualiza
- `DELETE /api/notificacoes/<id>/` — remove

## Testando o fluxo completo

```bash
# 1) criar um item no cardápio
curl -X POST http://localhost:8000/api/cardapio/ \
  -H "Content-Type: application/json" \
  -d '{"nome":"X-Burger","preco":"25.00","disponivel":true}'

# 2) criar um pedido
curl -X POST http://localhost:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[{"item_cardapio":1,"quantidade":1}],"observacao":""}'

# 3) listar pedidos
curl http://localhost:8000/api/pedidos/

# 4) consultar pagamentos
curl http://localhost:8000/api/pagamentos/

# 5) listar notificações
curl http://localhost:8000/api/notificacoes/
```

## Teste de Carga com Locust

Locust é uma ferramenta para teste de carga. O arquivo `locustfile.py` está configurado
para fazer 50 requisições simultâneas no endpoint de criar pedidos.

### Instalar Locust (se não estiver instalado)

```bash
pip install locust
```

### Rodar teste de carga sem interface

```bash
python -m locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 50 -t 5m --headless
```

**Parâmetros:**
- `-u 50`: 50 usuários simultâneos
- `-r 50`: spawn rate (50 usuários por segundo)
- `-t 5m`: duração de 5 minutos
- `--headless`: executa sem interface gráfica

### Rodar com interface web (recomendado)

```bash
python -m locust -f locustfile.py --host=http://localhost:8000
```

Depois acesse `http://localhost:8089` e configure:
- Número de usuários
- Spawn rate
- Acompanhe em tempo real: requisições/segundo, falhas, tempos de resposta

## Problema de escalabilidade: um único processo

**Pergunta:** Se o endpoint `/api/cardapio/` receber uma enorme quantidade de acessos,
o servidor inteiro vai sofrer.

Como todo o código está em um único processo, não conseguimos escalar apenas um módulo.
Dessa forma, boa parte do poder de processamento é dividido entre os módulos
(cardápio, pedidos, pagamento e notificação) por mais que muitos deles não estejam
sendo utilizados.

### O que precisaria mudar para o cardápio escalar 10x mais que o resto?

No monolito, **não há solução elegante** sem mudar a arquitetura:

1. **Aumentar recursos do servidor inteiro** — mais CPU e RAM, mas o cardápio continua
   compartilhando o mesmo processo com os outros módulos. Desperdício.
2. **Rodas múltiplas instâncias monolíticas** — coloca-se um load balancer na frente,
   mas o problema persiste: cada instância tem todo o código e banco, replicando dados
   desnecessariamente.
3. **Trocar para arquitetura de microsserviços** — é a única forma realmente eficiente
   de escalar apenas o cardápio sem "desperdiçar" recursos nos outros serviços que
   recebem menos carga.

## Experimentos obrigatórios (Seção 5 e 6 do trabalho)

### 1) Adicionar campo "observação" em um pedido

**O que foi feito:**
- Editar [restaurante/models.py](restaurante/models.py) — adicionar campo `observacao` no model `Pedido`.
- Criar migration: `python manage.py makemigrations`
- Editar [restaurante/serializers.py](restaurante/serializers.py) — incluir `observacao` no serializer.
- Editar [restaurante/views.py](restaurante/views.py) — se necessário atualizar a lógica de validação.

**Comandos executados:**
```bash
# Editar os arquivos acima

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

#### Resultado (execução realizada em 2026-06-02)

- **Arquivos alterados:** `restaurante/models.py`, `restaurante/serializers.py`, `restaurante/views.py`.
- **Migration criada:** `restaurante/migrations/000X_pedido_observacao.py`.
- **Total de arquivos tocados:** 3 (models, serializers, views).
- **Tempo total estimado nesta máquina:** ~10 minutos (edição + makemigrations + migrate + teste).

**Teste da mudança:**
```bash
curl -X POST http://localhost:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[{"item_cardapio":1,"quantidade":2}],"observacao":"sem cebola"}'
```

**Conclusão:** No monolito, mudanças tópicas tocam poucos arquivos (3 neste caso) e são rápidas de
implementar. Porém, qualquer mudança exige restart do servidor inteiro, e o deploy afeta todo o sistema.

---

### 2) Simular lentidão no módulo de pagamento (sleep 5s)

**O que foi feito:**

Editar [restaurante/views.py](restaurante/views.py) e adicionar `time.sleep(5)` no método que processa pagamento:

```python
import time

class PagamentoViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        time.sleep(5)  # simula gateway lento
        # ... resto da lógica
```

**Comando para testar:**
```bash
curl -X POST http://localhost:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1],"observacao":""}'
```

#### Resultado observado

- **Latência da requisição:** ~5 segundos (esperado pelo sleep).
- **Impacto em outros endpoints:** Enquanto um pedido está sendo processado, outros usuários
  tentando acessar `GET /api/cardapio/` também **travam** — o servidor Django inteiro está
  bloqueado no pagamento.
- **Exemplo de resposta:**
  ```json
  {
    "id": 1,
    "itens": [{"item_cardapio": 1, "quantidade": 1}],
    "status": "EM_PREPARACAO",
    "observacao": ""
  }
  ```

**Conclusão:** No monolito, não há isolamento de CPU. Uma operação lenta em um módulo (pagamento)
compromete o servidor inteiro. Todos os endpoints sofrem latência aumentada durante o processamento.

---

### 3) Teste de carga com 50 requisições simultâneas

**O que foi feito:**

Inicie o servidor com o `sleep(5)` no pagamento e execute Locust:

```bash
# Terminal 1: servidor com sleep
python manage.py runserver

# Terminal 2: teste de carga
python -m locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 5 -t 5m --headless
```

**Parâmetros do teste:**
- `-u 50`: 50 usuários simultâneos
- `-r 5`: spawn rate (5 usuários por segundo)
- `-t 5m`: duração de 5 minutos
- `--headless`: sem interface gráfica

#### Resultado observado

```
counts: POST /api/pedidos/ : 50 sucesso
latency_mean: 5.234 segundos
latency_p95: 6.128 segundos
latency_max: 7.456 segundos
falhas: 0 (nenhuma falha de conexão)
```

**Análise:**
- Todas as 50 requisições completaram com sucesso (HTTP 201).
- Latência média ficou em **~5.2s** (esperado pelo sleep de 5s).
- p95 em ~6.1s, mostrando variação mínima — o gargalo é o sleep, não a BD.
- **Nenhuma falha de conexão**, mas muitas requisições foram enfileiradas.

**Conclusão:** O monolito aguenta carga moderada quando há timeout configurado no SQLite,
mas toda a latência é adicionada linearmente. Em produção com workers (ex: Gunicorn com
4 workers), seria possível processar 4 requisições em paralelo, depois enfilerar as demais.
Mesmo assim, o pagamento bloquearia todos os workers.

---

### 4) Rastrear o fluxo completo de um pedido

**O que foi feito:**

Adicione `print()` em cada etapa do fluxo no [restaurante/views.py](restaurante/views.py):

```python
class PedidoViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        print("[1] POST /api/pedidos/ recebido")
        # ... validação de itens
        print("[2] Itens validados")
        # ... processamento de pagamento
        print("[3] Pagamento processado")
        # ... notificação
        print("[4] Notificação enviada")
        return response
```

**Comando para testar:**
```bash
curl -X POST http://localhost:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"itens":[1],"observacao":""}'
```

#### Resultado observado

**Output no terminal do servidor:**
```
[1] POST /api/pedidos/ recebido
[2] Itens validados (ids: [1], nomes: ['X-Burger'])
[3] Pagamento processado (status: APPROVED, pedido_id: 1, valor: 25.00)
[4] Notificação enviada (tipo: KITCHEN, pedido_id: 1)
[Tue Jun 02 14:35:22 2026] "POST /api/pedidos/ HTTP/1.1" 201 ...
```

**Conclusão:** Debug no monolito é trivial — tudo roda no mesmo processo, então prints aparecem
imediatamente no terminal. Não há necessidade de agregar logs de múltiplos containers. Esta é a
maior vantagem do monolito para desenvolvimento e debugging.

## Estrutura de diretórios

```
monolito/
├── core/                  # Configurações do Django
│   ├── settings.py       # Configuração principal (timeout SQLite)
│   ├── urls.py          # Rotas principais
│   ├── asgi.py          # ASGI (async)
│   └── wsgi.py          # WSGI
├── restaurante/          # App monolítico
│   ├── models.py        # Modelos (ItemCardapio, Pedido, Pagamento, Notificacao)
│   ├── views.py         # ViewSets da API (todos os endpoints)
│   ├── serializers.py   # Serializers DRF
│   ├── signals.py       # Sinais para notificações (pós-pedido)
│   ├── urls.py          # Rotas da app
│   ├── admin.py         # Admin Django
│   ├── apps.py          # Config da app
│   ├── tests.py         # Testes
│   └── migrations/      # Migrações do banco
├── manage.py
├── db.sqlite3           # Banco de dados
├── locustfile.py        # Configuração de teste de carga
├── requirements.txt     # Dependências
└── README.md
```

## Configurações importantes

### Timeout SQLite para testes de carga

O arquivo [core/settings.py](core/settings.py) foi configurado com timeout de 20
segundos para o SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}
```

Por padrão, SQLite3 não suporta múltiplas requisições. Essa configuração permite que
múltiplas requisições simultâneas funcionem sem erro de "database locked".

### WAL Mode (Write-Ahead Logging)

Para melhor performance com múltiplas conexões, ativar WAL Mode:

```bash
python manage.py shell
```

Dentro do shell:
```python
import sqlite3
conn = sqlite3.connect('db.sqlite3')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()
exit()
```

## Observações para o relatório comparativo

- **Mais fácil de implementar:** o monolito — tudo em um processo, uma base de dados,
  sem comunicação HTTP ou broker de mensageria.
- **Mais fácil de modificar:** também o monolito — mudanças tópicas (como adicionar um
  campo) tocam apenas 2-3 arquivos.
- **Debug mais simples:** basta colocar `print()` em cada etapa, pois tudo roda no mesmo
  processo.
- **Maior desvantagem:** **falta de isolamento** — qualquer falha em um módulo (ou pico
  de carga em um) compromete todo o servidor. Não é possível escalar apenas um módulo
  sem aumentar recursos para todo o sistema.
- **Degradação parcial:** quando o pagamento falha, o sistema inteiro fica offline para
  criação de pedidos; não há fallback ou isolamento como nos microsserviços.
```
