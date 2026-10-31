const hashPassword = require('../services/password_hasher');

class LmsController {
    constructor(model, cache = new Map(), logger = console) {
        this.model = model;
        this.cache = cache;
        this.logger = logger;
    }

    async checkout(input) {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card } = input;
        if (!name || !email || !courseId || !card) {
            return { status: 400, body: 'Bad Request' };
        }

        let course;
        try {
            course = await this.model.findActiveCourse(courseId);
        } catch {
            return { status: 404, body: 'Curso não encontrado' };
        }
        if (!course) return { status: 404, body: 'Curso não encontrado' };

        let user;
        try {
            user = await this.model.findUserByEmail(email);
        } catch {
            return { status: 500, body: 'Erro DB' };
        }

        let userId = user?.id;
        if (!userId) {
            try {
                userId = (await this.model.createUser(name, email, hashPassword(password || '123456'))).lastID;
            } catch {
                return { status: 500, body: 'Erro ao criar usuário' };
            }
        }

        const maskedCard = `${'*'.repeat(Math.max(card.length - 4, 0))}${card.slice(-4)}`;
        this.logger.log(`Processando cartão ${maskedCard}`);
        const paymentStatus = card.startsWith('4') ? 'PAID' : 'DENIED';
        if (paymentStatus === 'DENIED') return { status: 400, body: 'Pagamento recusado' };

        let enrollment;
        try {
            enrollment = await this.model.createEnrollment(userId, courseId);
        } catch {
            return { status: 500, body: 'Erro Matrícula' };
        }
        try {
            await this.model.createPayment(enrollment.lastID, course.price, paymentStatus);
        } catch {
            return { status: 500, body: 'Erro Pagamento' };
        }
        try {
            await this.model.createAuditLog(courseId, userId);
        } catch (error) {
            this.logger.error('Falha ao registrar auditoria de checkout', error);
        }

        this.logger.log(`[LOG] Salvando no cache: last_checkout_${userId}`);
        this.cache.set(`last_checkout_${userId}`, course.title);
        return { status: 200, body: { msg: 'Sucesso', enrollment_id: enrollment.lastID } };
    }

    async financialReport() {
        try {
            return { status: 200, body: await this.model.financialReport() };
        } catch {
            return { status: 500, body: 'Erro DB' };
        }
    }

    async deleteUser(id) {
        try {
            await this.model.deleteUser(id);
            return { status: 200, body: 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.' };
        } catch {
            return { status: 500, body: 'Erro DB' };
        }
    }
}

module.exports = LmsController;
