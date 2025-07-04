from web3 import Web3
import asyncio
import logging
from typing import Dict, Optional
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GasOptimizer:
    def __init__(self, config: Dict):
        """Initialize GasOptimizer with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.chain_id = config['chain_id']
        self.default_gas_limit = config['gas_limit']
        self.max_gas_price_gwei = config.get('max_gas_price_gwei', 100)
        self.min_gas_price_gwei = config.get('min_gas_price_gwei', 20)
        self.gas_price_samples = config.get('gas_price_samples', 10)

    async def get_optimal_gas_price(self) -> Optional[int]:
        """Dynamically calculate optimal gas price based on recent blocks."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return None

            # Collect gas prices from recent transactions
            gas_prices = []
            latest_block = await asyncio.to_thread(self.w3.eth.get_block, 'latest')
            for block_number in range(latest_block['number'], max(latest_block['number'] - self.gas_price_samples, 0), -1):
                block = await asyncio.to_thread(self.w3.eth.get_block, block_number, full_transactions=True)
                for tx in block['transactions']:
                    gas_price_gwei = self.w3.from_wei(tx['gasPrice'], 'gwei')
                    if self.min_gas_price_gwei <= gas_price_gwei <= self.max_gas_price_gwei:
                        gas_prices.append(gas_price_gwei)

            if not gas_prices:
                logger.warning("No valid gas prices found, using default")
                return self.w3.to_wei(self.min_gas_price_gwei, 'gwei')

            # Use median gas price for stability
            optimal_gas_price = statistics.median(gas_prices)
            optimal_gas_price_wei = self.w3.to_wei(min(optimal_gas_price, self.max_gas_price_gwei), 'gwei')
            logger.info(f"Optimal gas price calculated: {optimal_gas_price} gwei")
            return optimal_gas_price_wei

        except Exception as e:
            logger.error(f"Error calculating optimal gas price: {str(e)}")
            return self.w3.to_wei(self.min_gas_price_gwei, 'gwei')

    async def estimate_gas_limit(self, tx: Dict) -> Optional[int]:
        """Estimate gas limit for a transaction with a buffer."""
        try:
            estimated_gas = await asyncio.to_thread(self.w3.eth.estimate_gas, tx)
            # Add 20% buffer to avoid out-of-gas errors
            gas_limit = int(estimated_gas * 1.2)
            gas_limit = min(gas_limit, self.default_gas_limit)
            logger.info(f"Estimated gas limit: {gas_limit}")
            return gas_limit

        except Exception as e:
            logger.error(f"Error estimating gas limit: {str(e)}")
            return self.default_gas_limit

if platform.system() == "Emscripten":
    asyncio.ensure_future(GasOptimizer(config).get_optimal_gas_price())
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'chain_id': 1,
            'gas_limit': 200000,
            'max_gas_price_gwei': 100,
            'min_gas_price_gwei': 20,
            'gas_price_samples': 10
        }
        asyncio.run(GasOptimizer(config).get_optimal_gas_price())
