# Monolito Modular - trabalho-arquitetura

Este README documenta apenas a versão **monolito_modular** do projeto. O repositório também contém outras versões do sistema (por exemplo, `monolito` e a versão de microsserviços), mas este documento descreve apenas a aplicação modular monolítica.

## Visão geral

O `monolito_modular` é uma aplicação Django que organiza os domínios do sistema em módulos separados, cada um com sua própria interface pública.

Módulos disponíveis:
- `cardapio` - CRUD de itens do cardápio
- `pedidos` - criação, listagem e cancelamento de pedidos
- `pagamento` - processamento de pagamento mock e consulta de status
- `notificacao` - notificação da cozinha quando o pedido é pago

O objetivo desta versão é manter uma única aplicação e banco de dados, mas com fronteiras explícitas entre módulos.

## Arquitetura

- Aplicação única Django com um banco SQLite compartilhado.
- Cada domínio expõe sua própria interface de serviço:
  - `CardapioService`
  - `PedidoService`
  - `PagamentoService`
  - `NotificacaoService`
- Os módulos não acessam diretamente os repositórios/tabelas uns dos outros.
- A comunicação entre `pedidos` e outros módulos é feita via serviços públicos.

## Checklist de implementação

### Implementado
- [x] Aplicação única rodando em uma porta com Django
- [x] Banco único com todas as tabelas
- [x] Fluxo completo funcional: criar pedido → pagar → notificar cozinha
- [x] Endpoint de health check global (`GET /health/`)
- [x] Simulação de lentidão no pagamento (`sleep 5s` em `PagamentoService`)
- [x] Módulos com interfaces públicas separadas
- [x] Nenhum módulo acessa diretamente entidades de outro módulo
- [x] `notificacao` agora está implementado como app Django completo
- [x] Endpoint de listagem de pedidos
- [x] Endpoint de cancelamento de pedido

### Observações de limitação
- A separação de schema no banco é apenas simulada com `db_table` e prefixos de tabela.
- O sistema ainda usa SQLite, portanto não há verdadeiros schemas separados por módulo.
- A notificação não usa fila real; é chamada internamente após o pagamento.

## Dependências

As dependências estão em `requirements.txt`:
- Django==6.0.5
- djangorestframework==3.17.1
- asgiref==3.11.1
- sqlparse==0.5.5
- tzdata==2026.2

## Como rodar

1. Acesse o diretório:
   ```bash
   cd '/home/nathan/Área de trabalho/Atividade-Arquitetura/monolito_modular'
   ```

2. Ative o ambiente virtual (se houver):
   ```bash
   source ./venv/bin/activate
   ```

3. Instale dependências, se necessário:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações:
   ```bash
   ./venv/bin/python3 manage.py migrate
   ```

5. Inicie o servidor:
   ```bash
   ./venv/bin/python3 manage.py runserver 8000
   ```

O projeto estará disponível em `http://127.0.0.1:8000/`.

## Endpoints principais

### Health checks
- `GET /health/` - health check global do monolito modular
- `GET /pagamento/health/` - health check do módulo de pagamento
- `GET /notificacao/health/` - health check do módulo de notificação

### Pedidos
- `GET /pedidos/` - lista todos os pedidos
- `POST /pedidos/` - cria um pedido
  - Exemplo de payload:
    ```json
    {
      "itens": [1, 2, 3]
    }
    ```
- `DELETE /pedidos/<pedido_id>/` - cancela o pedido

### Pagamento
- `GET /pagamento/status/<pedido_id>/` - consulta status do pagamento do pedido

### Cardápio
- `GET /cardapio/itens/` - lista itens do cardápio
- `POST /cardapio/itens/` - cria item do cardápio
- `GET /cardapio/itens/<id>/` - obtém item do cardápio
- `PUT/PATCH /cardapio/itens/<id>/` - atualiza item do cardápio
- `DELETE /cardapio/itens/<id>/` - remove item do cardápio

## Como testar o fluxo pedido → pagamento → notificação

1. Crie itens do cardápio usando `POST /cardapio/itens/`.
2. Crie um pedido com IDs de itens válidos:
   - `POST /pedidos/` com payload `{ "itens": [1, 2] }`
3. O pedido será processado internamente:
   - valida itens via `CardapioService`
   - processa pagamento com `PagamentoService` (5s de delay)
   - notifica a cozinha via `NotificacaoService`

## O que foi ajustado neste módulo

- Corrigida a falta de `pagamento/urls.py`
- Adicionado serviço de notificação interno (`notificacao/services.py`)
- Adicionado app Django completo `notificacao` com URLs e views de health check
- Implementado listagem e cancelamento de pedidos no módulo `pedidos`
- Adicionada rota global `/health/`
- Verificado com `./venv/bin/python3 manage.py check`

## Estrutura de diretórios

- `cardapio/` - domínio do cardápio
- `pedidos/` - domínio de pedidos
- `pagamento/` - domínio de pagamento
- `notificacao/` - domínio de notificação
- `core/` - settings e rotas principais
- `db.sqlite3` - banco de dados SQLite compartilhado

## Observações finais

Esta versão é um **monolito modular**: tudo roda em um único processo e um único banco, mas com fronteiras explícitas entre domínios. Ela é útil para comparar contra a versão `monolito` tradicional e a versão de microsserviços do mesmo projeto.
