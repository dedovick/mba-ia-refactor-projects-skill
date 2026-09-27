function createCourseModel(db) {
    return {
        findActiveById(id) {
            return db.prepare('SELECT id, title, price FROM courses WHERE id = ? AND active = 1').get(id);
        },
        // Uma linha por matrícula (ou uma linha com matrícula nula para cursos sem alunos).
        listEnrollmentsWithPayments() {
            return db.prepare(`
                SELECT c.id AS course_id, c.title, e.id AS enrollment_id, u.name AS student_name,
                       p.amount, p.status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                ORDER BY c.id, e.id
            `).all();
        },
    };
}

module.exports = { createCourseModel };
