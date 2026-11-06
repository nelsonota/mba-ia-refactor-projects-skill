'use strict';

const express = require('express');
const { validateCheckout } = require('../middlewares/request_validation');
const { createAdminAuth } = require('../middlewares/admin_auth');

function createRoutes(controller, settings) {
    const router = express.Router();
    router.post('/checkout', validateCheckout, controller.checkout);
    router.get('/admin/financial-report', createAdminAuth(settings), controller.financialReport);
    router.delete('/users/:id', controller.deleteUser);
    return router;
}

module.exports = { createRoutes };
