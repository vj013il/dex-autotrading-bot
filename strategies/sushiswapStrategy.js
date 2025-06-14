const { ethers } = require('ethers');
const SushiSwapRouterABI = require('../contract/abis/SushiSwapRouter.json');

const router = new ethers.Contract(process.env.SUSHISWAP_ROUTER, SushiSwapRouterABI, provider);

async function swap(tokenIn, amountIn, dexToSell) {
  return await router.swapExactTokensForTokens(
    ethers.utils.parseUnits(amountIn.toString(), 18),
    0,
    [tokenIn, process.env.USDC_ADDRESS],
    process.env.CONTRACT_ADDRESS,
    Math.floor(Date.now() / 1000) + 1200,
    { gasLimit: 500000 }
  );
}

async function getPrice(tokenAddress) {
  // Placeholder: Use SushiSwap SDK
  return { buy: 1.01, sell: 1.03 };
}

module.exports = { swap, getPrice };
