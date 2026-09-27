const config = require('./config');
const { createLogger } = require('./config/logger');
const { createDatabase } = require('./database/connection');
const { initSchema } = require('./database/schema');
const passwordHasher = require('./services/passwordHasher');
const { createApp } = require('./app');

const logger = createLogger(config.logLevel);
const db = createDatabase(config);
initSchema(db, { passwordHasher });

createApp({ config, logger, db }).listen(config.port, () => {
    logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    if (!config.adminToken) logger.warn('ADMIN_TOKEN não definido: rotas administrativas estão bloqueadas.');
});
