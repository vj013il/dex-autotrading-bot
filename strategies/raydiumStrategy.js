const { Connection, PublicKey } = require('@solana/web3.js');

const connection = new Connection(process.env.SOLANA_RPC_URL);

async function swap(tokenIn, amountIn, dexToSell) {
  // Placeholder: Implement Raydium swap
  return { transactionId: '0x...' };
}

async function getPrice(tokenAddress) {
  return { buy: 1.00, sell: 1.02 };
}

module.exports = { swap, getPrice };
