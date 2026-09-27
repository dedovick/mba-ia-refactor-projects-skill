const { requirePositiveInteger } = require('./validators');
const { NotFoundError } = require('../middlewares/errorHandler');

function createUserController({ userService }) {
    return {
        delete(idParam) {
            const deleted = userService.deleteUser(requirePositiveInteger(idParam));
            if (!deleted) throw new NotFoundError('Usuário não encontrado');
        },
    };
}

module.exports = { createUserController };
