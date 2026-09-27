const { PAYMENT_STATUS } = require('../models/constants');

const UNKNOWN_STUDENT = 'Unknown';

class ReportService {
    constructor({ models }) {
        this.models = models;
    }

    financialReport() {
        const byCourse = new Map();
        for (const row of this.models.courses.findEnrollmentReportRows()) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { title: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const course = byCourse.get(row.course_id);
            if (row.payment_status === PAYMENT_STATUS.PAID) course.revenue += row.payment_amount;
            course.students.push({ name: row.student_name ?? UNKNOWN_STUDENT, paid: row.payment_amount ?? 0 });
        }
        return [...byCourse.values()];
    }
}

module.exports = ReportService;
