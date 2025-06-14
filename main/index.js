const server = require('./server');
const { logger } = require('../core/logger');

async function startBot() {
  try {
    logger.info('Starting DeFi Arbitrage Bot...');
    await server.start();
  } catch (error) {
    logger.error(`Failed to start bot: ${error.message}`);
    process.exit(1);
  }
}

startBot();
