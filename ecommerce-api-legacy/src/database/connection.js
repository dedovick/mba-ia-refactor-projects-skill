const { DatabaseSync } = require('node:sqlite');

function createDatabase(dbPath) {
    return new DatabaseSync(dbPath);
}

function transaction(db, work) {
    db.exec('BEGIN');
    try {
        const result = work();
        db.exec('COMMIT');
        return result;
    } catch (err) {
        db.exec('ROLLBACK');
        throw err;
    }
}

module.exports = { createDatabase, transaction };
