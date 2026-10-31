const { randomBytes, scryptSync } = require('node:crypto');

function hashPassword(password) {
    const salt = randomBytes(16);
    const derivedKey = scryptSync(password, salt, 32);
    return `${salt.toString('hex')}:${derivedKey.toString('hex')}`;
}

module.exports = hashPassword;
