const { ValidationError } = require('../middlewares/errorHandler');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+$/;
const DIGITS_PATTERN = /^\d+$/;

function requireString(value) {
    if (typeof value !== 'string' || value.trim() === '') throw new ValidationError();
    return value.trim();
}

function requireEmail(value) {
    const email = requireString(value);
    if (!EMAIL_PATTERN.test(email)) throw new ValidationError();
    return email;
}

function requireDigits(value) {
    const digits = requireString(value).replace(/[\s-]/g, '');
    if (!DIGITS_PATTERN.test(digits)) throw new ValidationError();
    return digits;
}

function requirePositiveInteger(value) {
    const isNumericString = typeof value === 'string' && DIGITS_PATTERN.test(value);
    const number = typeof value === 'number' || isNumericString ? Number(value) : NaN;
    if (!Number.isSafeInteger(number) || number <= 0) throw new ValidationError();
    return number;
}

module.exports = { requireString, requireEmail, requireDigits, requirePositiveInteger };
