const crypto = require('node:crypto');

const SALT_BYTES = 16;
const KEY_LENGTH = 64;

function hash(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derived = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${derived}`;
}

function verify(password, stored) {
    const [salt, expected] = String(stored || '').split(':');
    if (!salt || !expected || typeof password !== 'string') return false;
    const expectedBuffer = Buffer.from(expected, 'hex');
    const candidate = crypto.scryptSync(password, salt, expectedBuffer.length || KEY_LENGTH);
    return expectedBuffer.length === candidate.length && crypto.timingSafeEqual(expectedBuffer, candidate);
}

module.exports = { hash, verify };
