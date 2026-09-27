const { PAYMENT_STATUS } = require('../models/constants');

function createReportService({ courseModel }) {
    return {
        financialReport() {
            const byCourse = new Map();
            for (const row of courseModel.listEnrollmentsWithPayments()) {
                if (!byCourse.has(row.course_id)) {
                    byCourse.set(row.course_id, { title: row.title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue;

                const course = byCourse.get(row.course_id);
                if (row.status === PAYMENT_STATUS.PAID) course.revenue += row.amount;
                course.students.push({ name: row.student_name, paid: row.amount ?? 0 });
            }
            return [...byCourse.values()];
        },
    };
}

module.exports = { createReportService };
