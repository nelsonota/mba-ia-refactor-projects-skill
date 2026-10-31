const express = require('express');
const config = require('./config/settings');
const LmsModel = require('./models/lms_model');
const LmsController = require('./controllers/lms_controller');
const createRoutes = require('./views/routes');
const errorHandler = require('./middlewares/error_handler');

async function createApp({ model = new LmsModel(), cache = new Map(), logger = console } = {}) {
    await model.initialize();
    const controller = new LmsController(model, cache, logger);
    const app = express();
    app.use(express.json());
    app.use('/api', createRoutes(controller));
    app.use(errorHandler);
    return { app, model };
}

async function start() {
    const { app } = await createApp();
    return app.listen(config.port, () => console.log(`Frankenstein LMS rodando na porta ${config.port}...`));
}

if (require.main === module) {
    start().catch(error => {
        console.error('Application startup failed', error);
        process.exitCode = 1;
    });
}

module.exports = { createApp, start };
