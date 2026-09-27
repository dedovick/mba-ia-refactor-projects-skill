const express = require('express');
const passwordHasher = require('./services/passwordHasher');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createPaymentGateway } = require('./services/paymentGateway');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createRequireAdmin } = require('./middlewares/requireAdmin');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { buildRoutes } = require('./views/routes');

// Composition root: monta models, services, controllers e rotas com as dependências injetadas.
function createApp({ config, logger, db }) {
    const models = {
        userModel: createUserModel(db),
        courseModel: createCourseModel(db),
        enrollmentModel: createEnrollmentModel(db),
        paymentModel: createPaymentModel(db),
        auditLogModel: createAuditLogModel(db),
    };
    const paymentGateway = createPaymentGateway({ gatewayKey: config.paymentGatewayKey, logger });

    const checkoutService = createCheckoutService({ db, ...models, paymentGateway, passwordHasher });
    const reportService = createReportService(models);
    const userService = createUserService({ db, ...models });

    const app = express();
    app.use(express.json());
    app.use(buildRoutes({
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
        requireAdmin: createRequireAdmin(config),
    }));
    app.use(createErrorHandler(logger));
    return app;
}

module.exports = { createApp };
