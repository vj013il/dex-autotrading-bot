const { uniswapStrategy } = require('../strategies/uniswapStrategy');
const { sushiswapStrategy } = require('../strategies/sushiswapStrategy');

async function connectDEX(dexName) {
  switch (dexName) {
    case 'uniswap':
      return uniswapStrategy;
    case 'sushiswap':
      return sushiswapStrategy;
    default:
      throw new Error(`Unsupported DEX: ${dexName}`);
  }
}

module.exports = { connectDEX };
