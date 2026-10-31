const express = require('express');

function createRoutes(controller) {
    const router = express.Router();
    router.post('/checkout', async (req, res, next) => {
        try {
            const result = await controller.checkout(req.body || {});
            res.status(result.status);
            return typeof result.body === 'string' ? res.send(result.body) : res.json(result.body);
        } catch (error) { return next(error); }
    });
    router.get('/admin/financial-report', async (_req, res, next) => {
        try {
            const result = await controller.financialReport();
            res.status(result.status);
            return typeof result.body === 'string' ? res.send(result.body) : res.json(result.body);
        } catch (error) { return next(error); }
    });
    router.delete('/users/:id', async (req, res, next) => {
        try {
            const result = await controller.deleteUser(req.params.id);
            res.status(result.status);
            return res.send(result.body);
        } catch (error) { return next(error); }
    });
    return router;
}

module.exports = createRoutes;
