'use strict';

const port = Number(process.env.PORT || 3000);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('PORT must be an integer between 1 and 65535');
}

module.exports = Object.freeze({
    port,
    databasePath: process.env.DATABASE_PATH || ':memory:',
    adminApiToken: process.env.ADMIN_API_TOKEN || null,
    approvedCardPrefix: '4'
});
