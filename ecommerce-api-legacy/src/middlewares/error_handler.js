function errorHandler(error, _req, res, _next) {
    console.error('Unhandled request error', error);
    if (res.headersSent) return;
    if (error.status === 400 || error.statusCode === 400) {
        return res.status(400).send('Bad Request');
    }
    return res.status(500).send('Erro interno');
}

module.exports = errorHandler;
