const { ethers } = require('ethers');
const PancakeSwapRouterABI = require('../contract/abis/PancakeSwapRouter.json');

const router = new ethers.Contract(process.env.PANCAKESWAP_ROUTER, PancakeSwapRouterABI, provider);

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
  return { buy: 0.99, sell: 1.01 };
}

module.exports = { swap, getPrice };
