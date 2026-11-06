'use strict';

const Database = require('better-sqlite3');

class LmsModel {
    constructor(databasePath = ':memory:') {
        this.db = new Database(databasePath);
    }

    run(sql, params = []) {
        const result = this.db.prepare(sql).run(...params);
        return { lastId: result.lastInsertRowid, changes: result.changes };
    }

    get(sql, params = []) {
        return this.db.prepare(sql).get(...params);
    }

    all(sql, params = []) {
        return this.db.prepare(sql).all(...params);
    }

    async initialize() {
        await this.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
        await this.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
        await this.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
        await this.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
        await this.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

        const seededUser = await this.get('SELECT id FROM users WHERE email = ?', ['leonan@fullcycle.com.br']);
        if (!seededUser) {
            const userResult = await this.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                ['Leonan', 'leonan@fullcycle.com.br', null]
            );
            const courseIds = [];
            for (const course of [
                { title: 'Clean Architecture', price: 997.00 },
                { title: 'Docker', price: 497.00 }
            ]) {
                const result = await this.run(
                    'INSERT INTO courses (title, price, active) VALUES (?, ?, 1)',
                    [course.title, course.price]
                );
                courseIds.push(result.lastId);
            }
            const enrollment = await this.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userResult.lastId, courseIds[0]]
            );
            await this.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollment.lastId, 997.00, 'PAID']
            );
        }
    }

    findActiveCourse(courseId) {
        return this.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [courseId]);
    }

    findUserByEmail(email) {
        return this.get('SELECT id FROM users WHERE email = ?', [email]);
    }

    async createUser(name, email, passwordDigest) {
        const result = await this.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordDigest]
        );
        return result.lastId;
    }

    async createEnrollment(userId, courseId, coursePrice, paymentStatus) {
        const enrollment = await this.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
        await this.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollment.lastId, coursePrice, paymentStatus]
        );
        await this.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [`Checkout curso ${courseId} por ${userId}`]
        );
        return enrollment.lastId;
    }

    async getFinancialReport() {
        const rows = await this.all(
            `SELECT courses.id AS course_id, courses.title AS course_title,
                    enrollments.id AS enrollment_id, users.name AS student_name,
                    payments.amount AS payment_amount, payments.status AS payment_status
             FROM courses
             LEFT JOIN enrollments ON enrollments.course_id = courses.id
             LEFT JOIN users ON users.id = enrollments.user_id
             LEFT JOIN payments ON payments.enrollment_id = enrollments.id
             ORDER BY courses.id, enrollments.id`
        );
        const reportByCourse = new Map();
        for (const row of rows) {
            let courseReport = reportByCourse.get(row.course_id);
            if (!courseReport) {
                courseReport = { course: row.course_title, revenue: 0, students: [] };
                reportByCourse.set(row.course_id, courseReport);
            }
            if (row.enrollment_id !== null) {
                if (row.payment_status === 'PAID') courseReport.revenue += row.payment_amount;
                courseReport.students.push({
                    student: row.student_name || 'Unknown',
                    paid: row.payment_amount || 0
                });
            }
        }
        return Array.from(reportByCourse.values());
    }

    deleteUser(userId) {
        return this.run('DELETE FROM users WHERE id = ?', [userId]);
    }

    close() {
        this.db.close();
    }
}

module.exports = LmsModel;
