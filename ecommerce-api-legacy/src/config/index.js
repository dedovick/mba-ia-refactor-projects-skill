module.exports = Object.freeze({
    port: Number(process.env.PORT) || 3000,
    dbFilename: process.env.DB_FILENAME || ':memory:',
    adminToken: process.env.ADMIN_TOKEN || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    logLevel: process.env.LOG_LEVEL || 'info',
});
