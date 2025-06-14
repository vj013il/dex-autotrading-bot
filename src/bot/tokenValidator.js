const { ethers } = require('ethers');
const { apiClient } = require('../core/apiClient');

async function validateToken(tokenAddress) {
  try {
    const response = await apiClient.get(`https://api.etherscan.io/api?module=contract&action=getsourcecode&address=${tokenAddress}&apikey=${process.env.ETHERSCAN_API_KEY}`);
    if (response.data.result[0].SourceCode) {
      return true;
    }
    throw new Error('Invalid or unverified token contract');
  } catch (error) {
    throw new Error(`Token validation failed: ${error.message}`);
  }
}

module.exports = { validateToken };
