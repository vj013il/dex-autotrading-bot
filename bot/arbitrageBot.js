const { ethers } = require('ethers');
const { uniswapStrategy } = require('../strategies/uniswapStrategy');
const { sushiswapStrategy } = require('../strategies/sushiswapStrategy');
const { logger } = require('../core/logger');
const { telegramNotifier } = require('./telegramNotifier');

const provider = new ethers.providers.JsonRpcProvider(process.env.INFURA_URL);

async function executeArbitrage(tokenAddress, amountIn, minProfitPercent, dexToSell) {
  try {
    const prices = await fetchPrices(tokenAddress);
    const { buyDex, sellDex, priceDiff } = findArbitrageOpportunity(prices, minProfitPercent);

    if (priceDiff <= 0) {
      logger.info('No arbitrage opportunity found');
      return;
    }

    const tx = await uniswapStrategy.swap(tokenAddress, amountIn, dexToSell);
    await telegramNotifier.send(`Arbitrage executed: Profit ${priceDiff}, TX: ${tx.hash}`);
  } catch (error) {
    logger.error(`Arbitrage failed: ${error.message}`);
  }
}

async function fetchPrices(tokenAddress) {
  return {
    uniswap: await uniswapStrategy.getPrice(tokenAddress),
    sushiswap: await sushiswapStrategy.getPrice(tokenAddress)
  };
}

function findArbitrageOpportunity(prices, minProfitPercent) {
  let maxProfit = 0;
  let buyDex = null;
  let sellDex = null;

  for (const buyDexName in prices) {
    for (const sellDexName in prices) {
      if (buyDexName !== sellDexName) {
        const profit = prices[sellDexName].sell - prices[buyDexName].buy;
        if (profit > maxProfit && profit >= minProfitPercent / 100) {
          maxProfit = profit;
          buyDex = buyDexName;
          sellDex = sellDexName;
        }
      }
    }
  }

  return { buyDex, sellDex, priceDiff: maxProfit };
}

module.exports = { executeArbitrage };
