const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };

function createLogger(level = 'info') {
    const threshold = LEVELS[level] ?? LEVELS.info;
    const write = (name, stream) => (...args) => {
        if (LEVELS[name] >= threshold) stream(`[${new Date().toISOString()}] [${name}]`, ...args);
    };
    return {
        debug: write('debug', console.debug),
        info: write('info', console.info),
        warn: write('warn', console.warn),
        error: write('error', console.error),
    };
}

module.exports = { createLogger };
