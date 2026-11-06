'use strict';

class LmsController {
    constructor({ lmsModel, checkoutService }) {
        this.lmsModel = lmsModel;
        this.checkoutService = checkoutService;
    }

    checkout = async (req, res, next) => {
        try {
            const result = await this.checkoutService.checkout(req.validatedCheckout);
            return res.status(200).json(result);
        } catch (error) {
            return next(error);
        }
    };

    financialReport = async (_req, res, next) => {
        try {
            return res.status(200).json(await this.lmsModel.getFinancialReport());
        } catch (error) {
            return next(error);
        }
    };

    deleteUser = async (req, res, next) => {
        try {
            const deletion = await this.lmsModel.deleteUser(req.params.id);
            if (deletion.changes === 0) {
                return res.status(404).send('Usuário não encontrado');
            }
            return res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        } catch (error) {
            return next(error);
        }
    };
}

module.exports = LmsController;
