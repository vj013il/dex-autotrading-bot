import ccxt.async_support as ccxt
import asyncio
import json
import logging
from typing import Dict, List
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriceMonitor:
    def __init__(self, config: Config):
        self.config = config
        self.exchanges = {name: getattr(ccxt, name)({
            'apiKey': self.config.cex_api_keys.get(name, {}).get('apiKey'),
            'secret': self.config.cex_api_keys.get(name, {}).get('secret'),
            'enableRateLimit': True,
        }) for name in config.exchanges}

    async def fetch_prices(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        prices = {}
        for pair in self.config.pairs:
            prices[pair] = {}
            for name, exchange in self.exchanges.items():
                try:
                    ticker = await exchange.fetch_ticker(pair)
                    prices[pair][name] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'bid_volume': ticker.get('bidVolume', 0),
                        'ask_volume': ticker.get('askVolume', 0)
                    }
                except Exception as e:
                    logger.error(f"Error fetching prices from {name} for {pair}: {e}")
            # Save prices to shared storage (e.g., JSON file or Redis)
            with open('prices.json', 'w') as f:
                json.dump(prices, f)
        return prices

    async def run(self):
        while True:
            await self.fetch_prices()
            await asyncio.sleep(self.config.check_interval)

async def main():
    config = Config.load('config.json')
    monitor = PriceMonitor(config)
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())
