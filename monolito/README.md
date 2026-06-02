# Restaurante Monolito - Django API

API monolítica para gerenciamento de restaurante com suporte a pedidos, cardápio, pagamentos e notificações.


## 🚀 Instalação

### 1. Clonar o repositório

### 2. Criar ambiente virtual

No terminal:
python -m venv venv

### 3. Ativar ambiente virtual

No terminal (Windows)
.\venv\Scripts\activate

No terminal (Linux)
source venv/bin/activate

### 4. Instalar dependências

pip install -r requirements.txt


## ⚙️ Configuração

### Aplicar migrações do banco de dados
python manage.py migrate

### Criar usuário admin (opcional)

python manage.py createsuperuser

### Criar dados de teste (cardápio)

python manage.py shell

Depois execute:

from restaurante.models import ItemCardapio

ItemCardapio.objects.create(
    nome="Lasanha de carne",
    preco=5.50,
    disponivel=True
)

ItemCardapio.objects.create(
    nome="Coca Cola 350ml",
    preco=6.00,
    disponivel=True
)

ItemCardapio.objects.create(
    nome="Bolo de chocolate",
    preco=15.00,
    disponivel=True
)

exit()

## 🏃 Executar a aplicação

### Iniciar servidor Django

python manage.py runserver

O servidor estará disponível em: `http://localhost:8000`

### Acessar documentação da API (Swagger)

http://localhost:8000/api/docs/

### Acessar admin do Django

http://localhost:8000/admin/


## 🧪 Testes de Carga com Locust

Locust é uma ferramenta para teste de carga. O arquivo `locustfile.py` está configurado para fazer 50 requisições simultâneas no endpoint de criar pedidos.

### Instalar Locust (se não estiver instalado)

pip install locust

### Rodar teste de carga com 50 usuários

python -m locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 50 -t 5m --headless

**Parâmetros:**
- `-u 50`: 50 usuários simultâneos
- `-r 50`: spawn rate (50 usuários por segundo)
- `-t 5m`: duração de 5 minutos
- `--headless`: executa sem interface gráfica

### Rodar com interface web (recomendado)

python -m locust -f locustfile.py --host=http://localhost:8000

Depois acesse: `http://localhost:8089`

Nesta interface, você pode:
- Definir número de usuários
- Definir spawn rate
- Acompanhar em tempo real: requisições/segundo, falhas, tempos de resposta

## 📊 Endpoints da API

### Cardápio
- `GET /api/cardapio/` - Lista todos os itens
- `POST /api/cardapio/` - Criar novo item
- `GET /api/cardapio/{id}/` - Obter detalhes
- `PUT ou PATCH /api/cardapio/{id}/` - Atualizar item
- `DELETE /api/cardapio/{id}/` - Deletar item

### Pedidos
- `GET /api/pedidos/` - Listar todos os pagamentos
- `POST /api/pedidos/` - Criar novo pedido
- `GET /api/pedidos/{id}/` - Obter detalhes de um pedido
- `PUT ou PATCH /api/pedidos/{id}/` - Atualizar detalhes um pedido
- `POST /api/pedidos/{id}/cancelar/` - Cancelar um pedido

### Pagamentos
- `GET /api/pagamentos/` - Listar pagamentos
- `POST /api/pagamentos/` - Criar pagamento
- `PUT ou PATCH /api/pagamentos/{id}/` - Atualizar detalhes de pagamento
- `DELETE /api/pagamentos/{id}/` - Deletar pagamento

### Notificações
- `GET /api/notificacoes/` - Listar notificações
- `POST /api/notificacoes/` - Criar notificação
- `GET /api/notificacoes/{id}/` - Obter detalhes de uma notificação
- `PUT ou PATCH /api/notificacoes/{id}` - Atualizar detalhes de uma notificação
- `DELETE /api/notificacoes/{id}/` - Deleta uma notificação

## 🔧 Configurações Importantes

### Timeout SQLite para Testes de Carga

O arquivo `core/settings.py` foi configurado com timeout de 20 segundos para o SQLite:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

Por padrão, o SQLite3 não suporta múltiplas requisições. Essa configuração permite que múltiplas requisições simultâneas funcionem sem erro de "database locked".

### WAL Mode (Write-Ahead Logging)

Para melhor performance com múltiplas conexões, ativar WAL Mode:

No terminal:
python manage.py shell

import sqlite3
conn = sqlite3.connect('db.sqlite3')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()
exit()
```

## 📝 Exemplo de requisição (criar pedido)
{
    "itens": [
        {
        "item_cardapio": "1",
        "quantidade": 2
        }
    ],
    "observacao": "Sem cebola"
}

## 📦 Estrutura do Projeto

```
monolito/
├── core/                  # Configurações do Django
│   ├── settings.py       # Configuração principal
│   ├── urls.py          # Rotas principais
│   └── wsgi.py
├── restaurante/          # App principal
│   ├── models.py        # Modelos de dados
│   ├── views.py         # ViewSets da API
│   ├── serializers.py   # Serializers DRF
│   ├── urls.py          # Rotas da app
│   └── migrations/      # Migrações do banco
├── manage.py
├── db.sqlite3           # Banco de dados
├── locustfile.py        # Configuração de teste de carga
└── requirements.txt     # Dependências
```
