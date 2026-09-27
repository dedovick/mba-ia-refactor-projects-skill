const { transaction } = require('../database/connection');
const { PAYMENT_STATUS } = require('../models/constants');
const { NotFoundError, UnauthorizedError, ValidationError } = require('../middlewares/errorHandler');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel,
    paymentGateway, passwordHasher }) {
    return {
        checkout({ name, email, password, courseId, cardNumber }) {
            const course = courseModel.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            // Conta existente só é usada com a senha correta (antes de qualquer cobrança ou gravação).
            const existingUser = userModel.findByEmail(email);
            if (existingUser && !passwordHasher.verify(password, existingUser.pass)) {
                throw new UnauthorizedError('Credenciais inválidas');
            }

            const status = paymentGateway.charge(cardNumber, course.price);
            if (status !== PAYMENT_STATUS.PAID) throw new ValidationError('Pagamento recusado');

            return transaction(db, () => {
                const userId = existingUser
                    ? existingUser.id
                    : userModel.create({ name, email, passwordHash: passwordHasher.hash(password) });
                const enrollmentId = enrollmentModel.create(userId, course.id);
                paymentModel.create(enrollmentId, course.price, status);
                auditLogModel.create(`Checkout curso ${course.id} por ${userId}`);
                return { enrollmentId };
            });
        },
    };
}

module.exports = { createCheckoutService };
