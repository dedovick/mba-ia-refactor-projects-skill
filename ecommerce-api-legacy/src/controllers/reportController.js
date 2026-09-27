function createReportController({ reportService }) {
    return {
        financialReport() {
            return reportService.financialReport();
        },
    };
}

module.exports = { createReportController };
