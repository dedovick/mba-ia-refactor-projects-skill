const crypto = require('node:crypto');
const { UnauthorizedError } = require('./errorHandler');

const ADMIN_TOKEN_HEADER = 'X-Admin-Token';

function tokensMatch(provided, expected) {
    const a = Buffer.from(provided);
    const b = Buffer.from(expected);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Sem ADMIN_TOKEN configurado, as rotas administrativas ficam bloqueadas (fail closed).
function requireAdmin(adminToken) {
    return (req, res, next) => {
        const provided = req.get(ADMIN_TOKEN_HEADER) || '';
        if (!adminToken || !tokensMatch(provided, adminToken)) return next(new UnauthorizedError());
        return next();
    };
}

module.exports = { requireAdmin, ADMIN_TOKEN_HEADER };
