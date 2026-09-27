const { transaction } = require('../database/connection');
const { PAYMENT_STATUS } = require('../models/constants');
const { AppError, NotFoundError } = require('../middlewares/errorHandler');
const { hashPassword } = require('../utils/password');

class CheckoutService {
    constructor({ db, models, paymentGateway, logger }) {
        this.db = db;
        this.models = models;
        this.paymentGateway = paymentGateway;
        this.logger = logger;
    }

    // Decide o pagamento antes de gravar qualquer coisa; as gravações acontecem numa transação.
    checkout({ name, email, password, courseId, cardNumber }) {
        const { users, courses, enrollments, payments, auditLogs } = this.models;

        const course = courses.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const status = this.paymentGateway.charge(cardNumber, course.price);
        if (status === PAYMENT_STATUS.DENIED) throw new AppError('Pagamento recusado', 400);

        const enrollmentId = transaction(this.db, () => {
            const existing = users.findByEmail(email);
            const userId = existing
                ? existing.id
                : users.create({ name, email, passwordHash: password ? hashPassword(password) : null });
            const newEnrollmentId = enrollments.create(userId, course.id);
            payments.create(newEnrollmentId, course.price, status);
            auditLogs.record(`Checkout curso ${course.id} por ${userId}`);
            return newEnrollmentId;
        });

        this.logger.debug(`Checkout concluído: matrícula ${enrollmentId} no curso "${course.title}"`);
        return { enrollmentId };
    }
}

module.exports = CheckoutService;
