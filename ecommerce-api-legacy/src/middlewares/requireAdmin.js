const crypto = require('node:crypto');
const { UnauthorizedError, ForbiddenError } = require('./errorHandler');

const ADMIN_TOKEN_HEADER = 'X-Admin-Token';

function tokensMatch(provided, expected) {
    const a = Buffer.from(provided);
    const b = Buffer.from(expected);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Sem ADMIN_TOKEN configurado, as rotas administrativas ficam fechadas.
function createRequireAdmin({ adminToken }) {
    return (req, res, next) => {
        const provided = req.get(ADMIN_TOKEN_HEADER);
        if (!provided) return next(new UnauthorizedError());
        if (!adminToken || !tokensMatch(provided, adminToken)) return next(new ForbiddenError());
        return next();
    };
}

module.exports = { createRequireAdmin, ADMIN_TOKEN_HEADER };
