class AppError extends Error {
    constructor(message, status = 500) {
        super(message);
        this.status = status;
    }
}
class ValidationError extends AppError { constructor(message = 'Bad Request') { super(message, 400); } }
class UnauthorizedError extends AppError { constructor(message = 'Não autorizado') { super(message, 401); } }
class ForbiddenError extends AppError { constructor(message = 'Acesso negado') { super(message, 403); } }
class NotFoundError extends AppError { constructor(message) { super(message, 404); } }

// Mantém o formato de erro do projeto: texto puro com a mensagem.
function createErrorHandler(logger) {
    return (err, req, res, _next) => {
        if (err instanceof AppError) return res.status(err.status).send(err.message);
        if (err.status >= 400 && err.status < 500) {
            // Erros do body-parser (JSON inválido, payload grande): sem stack para o cliente.
            return res.status(err.status).send('Bad Request');
        }
        logger.error(err);
        return res.status(500).send('Erro interno');
    };
}

module.exports = { AppError, ValidationError, UnauthorizedError, ForbiddenError, NotFoundError, createErrorHandler };
