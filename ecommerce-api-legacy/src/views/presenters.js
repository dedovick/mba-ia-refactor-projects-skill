const USER_DELETED_MESSAGE = 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';

function presentCheckout({ enrollmentId }) {
    return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

function presentFinancialReport(courses) {
    return courses.map((course) => ({
        course: course.title,
        revenue: course.revenue,
        students: course.students.map((student) => ({ student: student.name, paid: student.paid })),
    }));
}

module.exports = { presentCheckout, presentFinancialReport, USER_DELETED_MESSAGE };
