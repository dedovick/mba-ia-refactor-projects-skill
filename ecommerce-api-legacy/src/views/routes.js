const express = require('express');
const { presentCheckout, presentFinancialReport, USER_DELETED_MESSAGE } = require('./presenters');

function buildRoutes({ checkoutController, reportController, userController, requireAdmin }) {
    const router = express.Router();

    router.post('/api/checkout', (req, res) => {
        const result = checkoutController.checkout(req.body);
        res.status(200).json(presentCheckout(result));
    });

    router.get('/api/admin/financial-report', requireAdmin, (req, res) => {
        res.json(presentFinancialReport(reportController.financialReport()));
    });

    router.delete('/api/users/:id', requireAdmin, (req, res) => {
        userController.delete(req.params.id);
        res.send(USER_DELETED_MESSAGE);
    });

    return router;
}

module.exports = { buildRoutes };
