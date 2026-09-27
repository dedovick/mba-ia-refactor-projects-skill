const express = require('express');
const { requireAdmin } = require('../middlewares/auth');
const { presentCheckout, presentFinancialReport, USER_DELETED_MESSAGE } = require('./presenters');

function buildRoutes({ controllers, config }) {
    const router = express.Router();
    const adminOnly = requireAdmin(config.adminToken);

    router.post('/api/checkout', (req, res) => {
        res.status(200).json(presentCheckout(controllers.checkout.checkout(req.body)));
    });

    router.get('/api/admin/financial-report', adminOnly, (req, res) => {
        res.json(presentFinancialReport(controllers.report.financialReport()));
    });

    router.delete('/api/users/:id', adminOnly, (req, res) => {
        controllers.user.deleteUser(req.params.id);
        res.send(USER_DELETED_MESSAGE);
    });

    return router;
}

module.exports = { buildRoutes };
