const { transaction } = require('./connection');
const { PAYMENT_STATUS } = require('../models/constants');

const SCHEMA = `
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
    CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
    CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
    CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
    CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
`;

// Seed idempotente: só roda com o banco vazio (em memória, a cada boot).
function initSchema(db, { passwordHasher }) {
    db.exec(SCHEMA);
    const { count } = db.prepare('SELECT COUNT(*) AS count FROM users').get();
    if (count > 0) return;

    transaction(db, () => {
        db.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)')
            .run('Leonan', 'leonan@fullcycle.com.br', passwordHasher.hash('123'));
        const insertCourse = db.prepare('INSERT INTO courses (title, price, active) VALUES (?, ?, 1)');
        insertCourse.run('Clean Architecture', 997.0);
        insertCourse.run('Docker', 497.0);
        db.prepare('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)').run();
        db.prepare('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)').run(PAYMENT_STATUS.PAID);
    });
}

module.exports = { initSchema };
