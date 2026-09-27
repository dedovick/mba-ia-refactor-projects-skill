const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../models/constants');

const maskCard = (cardNumber) => `**** ${cardNumber.slice(-4)}`;

// Gateway simulado. A chave vem da config e nunca é logada.
function createPaymentGateway({ gatewayKey, logger }) {
    if (!gatewayKey) logger.warn('PAYMENT_GATEWAY_KEY não definida: usando o gateway simulado.');
    return {
        charge(cardNumber, amount) {
            logger.info(`Processando pagamento de ${amount} com cartão ${maskCard(cardNumber)}`);
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentGateway };
