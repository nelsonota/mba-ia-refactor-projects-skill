'use strict';

function errorHandler(error, _req, res, _next) {
    const status = Number.isInteger(error.status) ? error.status : 500;
    const publicMessage = status === 500 ? 'Erro DB' : error.message;
    if (status === 500) console.error('[ERROR]', error.message);
    return res.status(status).send(publicMessage);
}

module.exports = { errorHandler };
