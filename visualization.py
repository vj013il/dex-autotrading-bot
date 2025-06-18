  import telegram
  import logging
  from dotenv import load_dotenv
  import os
  import asyncio

  load_dotenv()
  TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
  TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
  logger = logging.getLogger(__name__)

  async def send_telegram_notification(message):
      if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
          logger.warning("Telegram not configured")
          return
      try:
          bot = telegram.Bot(token=TELEGRAM_TOKEN)
          await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
          logger.info("Telegram notification sent")
      except Exception as e:
          logger.error(f"Error sending Telegram notification: {e}")
