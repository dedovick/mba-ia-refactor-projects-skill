function createEnrollmentModel(db) {
    return {
        create(userId, courseId) {
            return db.prepare('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)')
                .run(userId, courseId).lastInsertRowid;
        },
        deleteByUserId(userId) {
            return db.prepare('DELETE FROM enrollments WHERE user_id = ?').run(userId).changes;
        },
    };
}

module.exports = { createEnrollmentModel };
