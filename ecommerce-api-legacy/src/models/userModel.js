function createUserModel(db) {
    return {
        findByEmail(email) {
            return db.prepare('SELECT id, pass FROM users WHERE email = ?').get(email);
        },
        create({ name, email, passwordHash }) {
            return db.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)')
                .run(name, email, passwordHash).lastInsertRowid;
        },
        deleteById(id) {
            return db.prepare('DELETE FROM users WHERE id = ?').run(id).changes;
        },
    };
}

module.exports = { createUserModel };
