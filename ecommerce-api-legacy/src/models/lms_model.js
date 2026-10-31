const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('node:util');
const hashPassword = require('../services/password_hasher');

class LmsModel {
    constructor(database = new sqlite3.Database(':memory:')) {
        this.database = database;
        this.get = promisify(database.get.bind(database));
        this.all = promisify(database.all.bind(database));
        this.run = (sql, params = []) => new Promise((resolve, reject) => {
            database.run(sql, params, function (error) {
                if (error) return reject(error);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    async initialize() {
        const statements = [
            'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
            'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
            'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
            'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
            'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
            "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)",
            'INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)',
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')"
        ];
        for (const sql of statements.slice(0, 5)) await this.run(sql);
        await this.createUser('Leonan', 'leonan@fullcycle.com.br', hashPassword('123'));
        for (const sql of statements.slice(5)) await this.run(sql);
    }

    findActiveCourse(id) {
        return this.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    }

    findUserByEmail(email) {
        return this.get('SELECT id FROM users WHERE email = ?', [email]);
    }

    createUser(name, email, passwordHash) {
        return this.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
    }

    createEnrollment(userId, courseId) {
        return this.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
    }

    createPayment(enrollmentId, amount, status) {
        return this.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
    }

    createAuditLog(courseId, userId) {
        return this.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [`Checkout curso ${courseId} por ${userId}`]);
    }

    async financialReport() {
        const rows = await this.all(`
            SELECT courses.id AS course_id, courses.title AS course_title,
                   enrollments.id AS enrollment_id, users.name AS student_name,
                   payments.amount AS payment_amount, payments.status AS payment_status
            FROM courses
            LEFT JOIN enrollments ON enrollments.course_id = courses.id
            LEFT JOIN users ON users.id = enrollments.user_id
            LEFT JOIN payments ON payments.enrollment_id = enrollments.id
            ORDER BY courses.id DESC, enrollments.id
        `);
        const courses = new Map();
        for (const row of rows) {
            if (!courses.has(row.course_id)) {
                courses.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id !== null) {
                const item = courses.get(row.course_id);
                if (row.payment_status === 'PAID') item.revenue += row.payment_amount;
                item.students.push({ student: row.student_name || 'Unknown', paid: row.payment_amount ?? 0 });
            }
        }
        return [...courses.values()];
    }

    deleteUser(id) {
        return this.run('DELETE FROM users WHERE id = ?', [id]);
    }

    close() {
        return new Promise((resolve, reject) => this.database.close(error => error ? reject(error) : resolve()));
    }
}

module.exports = LmsModel;
