'use strict';

const crypto = require('node:crypto');

class CheckoutService {
    constructor({ lmsModel, settings }) {
        this.lmsModel = lmsModel;
        this.settings = settings;
    }

    async checkout({ userName, email, password, courseId, cardNumber }) {
        const course = await this.lmsModel.findActiveCourse(courseId);
        if (!course) {
            const error = new Error('Curso não encontrado');
            error.status = 404;
            throw error;
        }

        let user = await this.lmsModel.findUserByEmail(email);
        if (!user) {
            const salt = crypto.randomBytes(16);
            const digest = crypto.scryptSync(password, salt, 64);
            const passwordDigest = `${salt.toString('hex')}:${digest.toString('hex')}`;
            user = { id: await this.lmsModel.createUser(userName, email, passwordDigest) };
        }

        const paymentStatus = cardNumber.startsWith(this.settings.approvedCardPrefix) ? 'PAID' : 'DENIED';
        if (paymentStatus === 'DENIED') {
            const error = new Error('Pagamento recusado');
            error.status = 400;
            throw error;
        }

        const enrollmentId = await this.lmsModel.createEnrollment(
            user.id,
            courseId,
            course.price,
            paymentStatus
        );
        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }
}

module.exports = CheckoutService;
