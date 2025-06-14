const TelegramBot = require('node-telegram-bot-api');
const config = require('../config/config');

const bot = new TelegramBot(config.telegramToken, { polling: true });

async function send(message) {
  try {
    await bot.sendMessage(config.telegramChatId, message);
  } catch (error) {
    console.error(`Telegram notification failed: ${error.message}`);
  }
}

async function setup() {
  bot.on('message', (msg) => {
    console.log(`Received Telegram message: ${msg.text}`);
  });
}

module.exports = { send, setup };
