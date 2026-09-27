const DEFAULT_PORT = 3000;

const config = Object.freeze({
    port: Number(process.env.PORT) || DEFAULT_PORT,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    adminToken: process.env.ADMIN_TOKEN || '',
    logLevel: process.env.LOG_LEVEL || 'info',
});

module.exports = config;
