const { transaction } = require('../database/connection');

function createUserService({ db, userModel, enrollmentModel, paymentModel }) {
    return {
        // Remove o usuário com matrículas e pagamentos, sem deixar órfãos. Retorna false se não existia.
        deleteUser(userId) {
            return transaction(db, () => {
                paymentModel.deleteByUserId(userId);
                enrollmentModel.deleteByUserId(userId);
                return userModel.deleteById(userId) > 0;
            });
        },
    };
}

module.exports = { createUserService };
