const { ValidationError } = require('../middlewares/errorHandler');

function requireString(value) {
    if (typeof value !== 'string' || value.trim() === '') throw new ValidationError();
    return value.trim();
}

function optionalString(value) {
    if (value === undefined || value === null || value === '') return null;
    if (typeof value !== 'string') throw new ValidationError();
    return value;
}

function requireId(value) {
    const id = Number(value);
    if (!Number.isInteger(id) || id <= 0 || (typeof value === 'string' && value.trim() === '')) {
        throw new ValidationError();
    }
    return id;
}

module.exports = { requireString, optionalString, requireId };
