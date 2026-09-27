const { requireString, optionalString, requireId } = require('./validators');

class CheckoutController {
    constructor({ checkoutService }) {
        this.checkoutService = checkoutService;
    }

    checkout(body = {}) {
        const input = {
            name: requireString(body.usr),
            email: requireString(body.eml),
            password: optionalString(body.pwd),
            courseId: requireId(body.c_id),
            cardNumber: requireString(body.card),
        };
        return this.checkoutService.checkout(input);
    }
}

module.exports = CheckoutController;
