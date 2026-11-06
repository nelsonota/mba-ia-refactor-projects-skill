'use strict';

const crypto = require('node:crypto');

function createAdminAuth(settings) {
    return function requireAdmin(req, res, next) {
        if (!settings.adminApiToken) return res.status(503).send('Admin access is not configured');
        const match = /^Bearer (.+)$/i.exec(req.get('authorization') || '');
        if (!match) return res.status(401).send('Unauthorized');

        const suppliedToken = Buffer.from(match[1]);
        const configuredToken = Buffer.from(settings.adminApiToken);
        const valid = suppliedToken.length === configuredToken.length
            && crypto.timingSafeEqual(suppliedToken, configuredToken);
        if (!valid) return res.status(401).send('Unauthorized');
        return next();
    };
}

module.exports = { createAdminAuth };
