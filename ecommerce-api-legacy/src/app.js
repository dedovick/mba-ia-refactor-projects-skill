const express = require('express');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const PaymentGateway = require('./services/paymentGateway');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const { buildRoutes } = require('./views/routes');
const { createErrorHandler } = require('./middlewares/errorHandler');

// Composition root: monta models, services e controllers com as dependências injetadas.
function createApp({ config, db, logger }) {
    const models = {
        users: new UserModel(db),
        courses: new CourseModel(db),
        enrollments: new EnrollmentModel(db),
        payments: new PaymentModel(db),
        auditLogs: new AuditLogModel(db),
    };
    const paymentGateway = new PaymentGateway({ apiKey: config.paymentGatewayKey, logger });
    const controllers = {
        checkout: new CheckoutController({
            checkoutService: new CheckoutService({ db, models, paymentGateway, logger }),
        }),
        report: new ReportController({ reportService: new ReportService({ models }) }),
        user: new UserController({ models }),
    };

    const app = express();
    app.use(express.json());
    app.use(buildRoutes({ controllers, config }));
    app.use(createErrorHandler(logger));
    return app;
}

module.exports = { createApp };
