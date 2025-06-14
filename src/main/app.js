const { walletManager } = require('../bot/walletManager');
const { priceMonitor } = require('../bot/priceMonitor');
const { telegramNotifier } = require('../bot/telegramNotifier');
const config = require('../config/config');

async function initialize() {
  await walletManager.initialize(config.masterPassword);
  await priceMonitor.start();
  await telegramNotifier.setup();
}

module.exports = { initialize };
