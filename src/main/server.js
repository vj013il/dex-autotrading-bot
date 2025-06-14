const express = require('express');
const { logger } = require('../core/logger');
const { arbitrageBot } = require('../bot/arbitrageBot');
const config = require('../config/config');

const app = express();
app.use(express.json());

app.post('/api/arbitrage', async (req, res) => {
  const { tokenAddress, amountIn, minProfitPercent, dexToSell } = req.body;
  try {
    await arbitrageBot.executeArbitrage(tokenAddress, amountIn, minProfitPercent, dexToSell);
    res.status(200).json({ message: 'Arbitrage executed successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

function start() {
  app.listen(config.port, () => {
    logger.info(`Server running on port ${config.port}`);
  });
}

module.exports = { start };
