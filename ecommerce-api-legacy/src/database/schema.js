const { hashPassword } = require('../utils/password');
const { PAYMENT_STATUS } = require('../models/constants');
const { transaction } = require('./connection');

const SCHEMA = `
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
    CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
    CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
    CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
    CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
`;

const SEED_PASSWORD = '123';

function seed(db) {
    const { total } = db.prepare('SELECT COUNT(*) AS total FROM courses').get();
    if (total > 0) return;

    transaction(db, () => {
        db.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)')
            .run('Leonan', 'leonan@fullcycle.com.br', hashPassword(SEED_PASSWORD));
        const insertCourse = db.prepare('INSERT INTO courses (title, price, active) VALUES (?, ?, 1)');
        insertCourse.run('Clean Architecture', 997.0);
        insertCourse.run('Docker', 497.0);
        db.prepare('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)').run();
        db.prepare('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)').run(PAYMENT_STATUS.PAID);
    });
}

function initDatabase(db) {
    db.exec(SCHEMA);
    seed(db);
}

module.exports = { initDatabase };
