import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    # Integrações reais (e-mail, SMS, push) ainda não existem; os eventos são registrados em log.
    logger.info("Notificação de pedido criado: pedido=%s usuario=%s (email, sms, push)", pedido_id, usuario_id)


def pedido_aprovado(pedido_id):
    logger.info("Notificação: pedido %s aprovado, preparar envio", pedido_id)


def pedido_cancelado(pedido_id):
    logger.info("Notificação: pedido %s cancelado, devolver estoque", pedido_id)


ON_STATUS_CHANGE = {
    "aprovado": pedido_aprovado,
    "cancelado": pedido_cancelado,
}


def status_alterado(pedido_id, novo_status):
    handler = ON_STATUS_CHANGE.get(novo_status)
    if handler:
        handler(pedido_id)
