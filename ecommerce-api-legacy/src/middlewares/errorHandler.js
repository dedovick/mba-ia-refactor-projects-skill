class AppError extends Error {
    constructor(message, status = 500) {
        super(message);
        this.status = status;
    }
}

class ValidationError extends AppError {
    constructor(message = 'Bad Request') { super(message, 400); }
}

class NotFoundError extends AppError {
    constructor(message) { super(message, 404); }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Não autorizado') { super(message, 401); }
}

// Mantém o formato de erro original da API: texto puro com a mensagem.
function createErrorHandler(logger) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (err instanceof AppError) return res.status(err.status).send(err.message);
        if (err.type === 'entity.parse.failed') return res.status(400).send('Bad Request');
        logger.error(`Erro inesperado em ${req.method} ${req.originalUrl}`, err);
        return res.status(500).send('Erro interno');
    };
}

module.exports = { AppError, ValidationError, NotFoundError, UnauthorizedError, createErrorHandler };
