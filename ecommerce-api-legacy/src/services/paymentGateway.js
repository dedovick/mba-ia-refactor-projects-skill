const { PAYMENT_STATUS } = require('../models/constants');

// Gateway simulado: cartões iniciados por este prefixo são aprovados.
const APPROVED_CARD_PREFIX = '4';

function maskCard(cardNumber) {
    return `**** ${String(cardNumber).slice(-4)}`;
}

class PaymentGateway {
    constructor({ apiKey, logger }) {
        this.apiKey = apiKey;
        this.logger = logger;
    }

    charge(cardNumber, amount) {
        this.logger.info(`Processando pagamento de ${amount} com cartão ${maskCard(cardNumber)}`);
        return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = PaymentGateway;
