const { uniswapStrategy } = require('../strategies/uniswapStrategy');
const { sushiswapStrategy } = require('../strategies/sushiswapStrategy');
const { logger } = require('../core/logger');

async function start() {
  setInterval(async () => {
    try {
      const tokenAddress = process.env.TOKEN_ADDRESS;
      const prices = {
        uniswap: await uniswapStrategy.getPrice(tokenAddress),
        sushiswap: await sushiswapStrategy.getPrice(tokenAddress)
      };
      logger.info(`Prices: ${JSON.stringify(prices)}`);
    } catch (error) {
      logger.error(`Price monitoring failed: ${error.message}`);
    }
  }, 60000); // Check every minute
}

module.exports = { start };
