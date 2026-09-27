class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return this.db.prepare('SELECT id, name, email FROM users WHERE email = ?').get(email);
    }

    create({ name, email, passwordHash }) {
        const { lastInsertRowid } = this.db
            .prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)')
            .run(name, email, passwordHash);
        return Number(lastInsertRowid);
    }

    deleteById(id) {
        return this.db.prepare('DELETE FROM users WHERE id = ?').run(id).changes;
    }
}

module.exports = UserModel;
