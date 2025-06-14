const { ethers } = require('ethers');
const UniswapV3RouterABI = require('../contract/abis/UniswapV3Router.json');

const router = new ethers.Contract(process.env.UNISWAP_ROUTER, UniswapV3RouterABI, provider);

async function swap(tokenIn, amountIn, dexToSell) {
  const params = {
    tokenIn,
    tokenOut: process.env.USDC_ADDRESS,
    fee: 3000,
    recipient: process.env.CONTRACT_ADDRESS,
    deadline: Math.floor(Date.now() / 1000) + 1200,
    amountIn: ethers.utils.parseUnits(amountIn.toString(), 18),
    amountOutMinimum: 0,
    sqrtPriceLimitX96: 0
  };
  return await router.exactInputSingle(params, { gasLimit: 500000 });
}

async function getPrice(tokenAddress) {
  // Placeholder: Use Uniswap V3 Quoter
  return { buy: 1.00, sell: 1.02 };
}

module.exports = { swap, getPrice };
