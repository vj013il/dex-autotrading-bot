const { ethers } = require('ethers');
const ArbitrageBotABI = require('../contract/abis/ArbitrageBot.json');

const provider = new ethers.providers.JsonRpcProvider(process.env.INFURA_URL);
const contract = new ethers.Contract(process.env.CONTRACT_ADDRESS, ArbitrageBotABI, provider);

async function executeTransaction(wallet, params) {
  const contractWithSigner = contract.connect(wallet);
  const tx = await contractWithSigner.executeArbitrage(
    params.tokenIn,
    params.tokenOut,
    params.amountIn,
    params.minProfit,
    params.dexToSell,
    { gasLimit: 500000 }
  );
  return await tx.wait();
}

module.exports = { executeTransaction };
