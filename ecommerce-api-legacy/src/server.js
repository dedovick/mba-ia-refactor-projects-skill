const config = require('./config');
const { createDatabase } = require('./database/connection');
const { initDatabase } = require('./database/schema');
const { createApp } = require('./app');
const { createLogger } = require('./utils/logger');

const logger = createLogger(config.logLevel);
const db = createDatabase(config.dbPath);
initDatabase(db);

if (!config.adminToken) logger.warn('ADMIN_TOKEN não configurado: rotas administrativas responderão 401.');

createApp({ config, db, logger }).listen(config.port, () => {
    logger.info(`LMS API rodando na porta ${config.port}`);
});
