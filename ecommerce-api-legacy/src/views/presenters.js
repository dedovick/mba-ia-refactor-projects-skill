const UNKNOWN_STUDENT = 'Unknown';
const USER_DELETED_MESSAGE = 'Usuário deletado.';

function presentCheckout({ enrollmentId }) {
    return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

function presentFinancialReport(courses) {
    return courses.map((course) => ({
        course: course.title,
        revenue: course.revenue,
        students: course.students.map((s) => ({ student: s.name ?? UNKNOWN_STUDENT, paid: s.paid })),
    }));
}

module.exports = { presentCheckout, presentFinancialReport, USER_DELETED_MESSAGE };
