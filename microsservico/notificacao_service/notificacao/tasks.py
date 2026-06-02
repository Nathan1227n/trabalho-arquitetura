from celery import shared_task

from .models import Notification


@shared_task(name='notificacao.notificar_cozinha')
def notificar_cozinha(order_id, message):
    """
    Task consumida pelo worker Celery (fila assincrona via RabbitMQ).

    Quando o servico de pedidos confirma o pagamento, ele publica esta task.
    Aqui registramos a notificacao na tabela e "avisamos" a cozinha.
    """
    notification = Notification.objects.create(
        order_id=order_id,
        message=message,
        status='SENT',
    )
    print(f"Cozinha avisada sobre o pedido {order_id}: {message}")
    return notification.id
