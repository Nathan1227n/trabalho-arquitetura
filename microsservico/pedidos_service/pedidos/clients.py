"""
Clientes HTTP para os outros microsservicos.

Estrategia de resiliencia: TIMEOUT EXPLICITO em toda chamada (connect, read).
Se um servico nao responde dentro do tempo, a chamada falha rapido e de forma
controlada em vez de travar o servico de pedidos indefinidamente.
"""

import requests
from django.conf import settings

# Timeout explicito (connect, read), em segundos.
# O read do pagamento e maior porque o mock dorme 5s simulando o gateway.
CARDAPIO_TIMEOUT = (3, 5)
PAGAMENTO_TIMEOUT = (3, 15)


class ServiceUnavailable(Exception):
    """Lancada quando um servico dependente nao responde (timeout/conexao)."""
    pass


def obter_item(item_id):
    """Busca um item no servico de Cardapio. Retorna o dict do item ou None (404)."""
    url = f"{settings.CARDAPIO_URL}/cardapio/itens/{item_id}/"
    try:
        response = requests.get(url, timeout=CARDAPIO_TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ServiceUnavailable(f"Servico de cardapio indisponivel: {exc}")

    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def processar_pagamento(order_id, amount):
    """Processa o pagamento no servico de Pagamento (chamada SINCRONA via HTTP)."""
    url = f"{settings.PAGAMENTO_URL}/pagamento/processar/"
    try:
        response = requests.post(
            url,
            json={"order_id": order_id, "amount": amount},
            timeout=PAGAMENTO_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        raise ServiceUnavailable(f"Servico de pagamento indisponivel: {exc}")

    response.raise_for_status()
    return response.json()
