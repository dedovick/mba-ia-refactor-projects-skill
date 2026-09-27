const { requireString, requireEmail, requireDigits, requirePositiveInteger } = require('./validators');

function createCheckoutController({ checkoutService }) {
    return {
        // Os nomes dos campos (usr, eml, pwd, c_id, card) são o contrato público da API.
        checkout(body) {
            const input = body && typeof body === 'object' ? body : {};
            return checkoutService.checkout({
                name: requireString(input.usr),
                email: requireEmail(input.eml),
                password: requireString(input.pwd),
                courseId: requirePositiveInteger(input.c_id),
                cardNumber: requireDigits(input.card),
            });
        },
    };
}

module.exports = { createCheckoutController };
