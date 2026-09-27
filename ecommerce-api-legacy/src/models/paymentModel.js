function createPaymentModel(db) {
    return {
        create(enrollmentId, amount, status) {
            return db.prepare('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)')
                .run(enrollmentId, amount, status).lastInsertRowid;
        },
        deleteByUserId(userId) {
            return db.prepare(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)'
            ).run(userId).changes;
        },
    };
}

module.exports = { createPaymentModel };
