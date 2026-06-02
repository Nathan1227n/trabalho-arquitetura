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

## Estratégia de resiliência (limitações do monolito)

No monolito, **não há isolamento real**. Se um módulo falha, tudo compromete-se:

- **Se pagamento falha:** O endpoint de criar pedido retorna erro, e os usuários não
  conseguem fazer novos pedidos. O sistema degrada-se como um todo.
- **Se notificação falha:** Também trava a criação de pedidos (porque notificação é
  chamada sincronamente durante o fluxo).
- **Debug é direto:** Rastrear o fluxo no monólito foi bem fácil já que tudo roda no mesmo processo do 
  Django. Colocamos um print() em cada etapa do fluxo (na criação do pedido, no recebimento do pagamento e 
  na criação da notificação) e conseguimos encontrar o erro a partir do terminal da aplicação.

## Experimentos obrigatórios 

### Simular lentidão no módulo de pagamento (sleep 5s)


### Resultado: todo o servidor fica lento

Ao criar um pedido (que dispara pagamento), a requisição **leva 5 segundos**. Durante
esse tempo:

- Outros usuários tentando acessar `/api/cardapio/` também **travam** — o único processo
  Django está ocupado processando pagamento.
- A thread/worker que atende a criação de pedido fica bloqueada por 5 segundos.
- Se o servidor tem apenas 1 worker (desenvolvimento), **ninguém consegue fazer nada**
  enquanto o pagamento está sendo processado.

**Degradação do sistema inteiro — não apenas do pagamento.**

### Teste de carga durante a simulação de lentidão

1. Inicie o servidor com o `sleep(5)` no pagamento
2. Execute Locust com 50 usuários:
```bash
python -m locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 2
```

**Observações:**
- Requisições são **enfileiradas** no servidor.
- A latência média sobe drasticamente (vai para +5s por pedido).
- Se tiver muitas requisições simultâneas, muitas podem dar timeout.
- **Endpoitns de leitura** (GET `/api/cardapio/`) também ficam lentes, pois compartilham
  o mesmo pool de workers.


### Adicionar campo "observação" em um pedido

**Trabalho no monolito:**
- Editar [restaurante/models.py](restaurante/models.py) — adicionar campo `observacao` no model `Pedido`.
- Criar migration: `python manage.py makemigrations`
- Editar [restaurante/serializers.py](restaurante/serializers.py) — incluir `observacao` no serializer.
- Editar [restaurante/views.py](restaurante/views.py) — se necessário atualizar a lógica de validação.

**Total: ~2-3 arquivos tocados, ~10 minutos.**

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
