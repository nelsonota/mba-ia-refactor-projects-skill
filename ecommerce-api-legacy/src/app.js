'use strict';

const express = require('express');
const settings = require('./config/settings');
const LmsModel = require('./models/lms_model');
const CheckoutService = require('./services/checkout_service');
const LmsController = require('./controllers/lms_controller');
const { createRoutes } = require('./views/routes');
const { errorHandler } = require('./middlewares/error_handler');

function createApp({ model, appSettings = settings } = {}) {
    const lmsModel = model || new LmsModel(appSettings.databasePath);
    const app = express();
    app.use(express.json());

    const checkoutService = new CheckoutService({ lmsModel, settings: appSettings });
    const controller = new LmsController({ lmsModel, checkoutService });
    app.use('/api', createRoutes(controller, appSettings));
    app.use(errorHandler);
    return { app, model: lmsModel };
}

async function start() {
    const model = new LmsModel(settings.databasePath);
    await model.initialize();
    const { app } = createApp({ model });
    const server = app.listen(settings.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
    });
    return { app, model, server };
}

if (require.main === module) {
    start().catch(error => {
        console.error('[STARTUP ERROR]', error.message);
        process.exitCode = 1;
    });
}

module.exports = { createApp, start };
