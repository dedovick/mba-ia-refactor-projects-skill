function createAuditLogModel(db) {
    return {
        create(action) {
            return db.prepare("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))")
                .run(action).lastInsertRowid;
        },
    };
}

module.exports = { createAuditLogModel };
