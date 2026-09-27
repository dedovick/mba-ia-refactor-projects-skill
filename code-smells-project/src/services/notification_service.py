import logging

from src.config.constants import STATUS_APROVADO, STATUS_CANCELADO

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    # Integrações reais (e-mail, SMS, push) entram aqui; hoje os envios são simulados no log.
    logger.info("Pedido %s criado para o usuário %s: notificações enviadas (email, sms, push)",
                pedido_id, usuario_id)


def _pedido_aprovado(pedido_id):
    logger.info("Pedido %s aprovado: preparar envio", pedido_id)


def _pedido_cancelado(pedido_id):
    logger.info("Pedido %s cancelado: devolver estoque", pedido_id)


_AO_MUDAR_STATUS = {
    STATUS_APROVADO: _pedido_aprovado,
    STATUS_CANCELADO: _pedido_cancelado,
}


def status_alterado(pedido_id, status):
    if notificar := _AO_MUDAR_STATUS.get(status):
        notificar(pedido_id)
