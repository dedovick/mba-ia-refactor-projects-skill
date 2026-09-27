class UserController {
    constructor({ models }) {
        this.users = models.users;
    }

    // Mantém o comportamento original: responde sucesso mesmo se o id não existir
    // e não remove matrículas/pagamentos do usuário.
    deleteUser(rawId) {
        this.users.deleteById(rawId);
    }
}

module.exports = UserController;
