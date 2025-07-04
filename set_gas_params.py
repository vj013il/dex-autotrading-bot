from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GasParams:
    def __init__(self, config: Dict):
        """Initialize GasParams with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.chain_id = config['chain_id']
        self.default_gas_limit = config['gas_limit']
        self.default_gas_price_gwei = config['gas_price_gwei']

    async def set_gas_parameters(self, tx: Dict, custom_gas_price_gwei: Optional[float] = None, custom_gas_limit: Optional[int] = None) -> Dict:
        """Set gas parameters for a transaction."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return tx

            # Use custom gas price if provided, else use GasOptimizer
            gas_optimizer = GasOptimizer(config)
            gas_price = self.w3.to_wei(custom_gas_price_gwei, 'gwei') if custom_gas_price_gwei else await gas_optimizer.get_optimal_gas_price()
            gas_limit = custom_gas_limit if custom_gas_limit else await gas_optimizer.estimate_gas_limit(tx)

            # Update transaction with gas parameters
            tx.update({
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': self.chain_id
            })

            logger.info(f"Gas parameters set: gasPrice={self.w3.from_wei(gas_price, 'gwei')} gwei, gasLimit={gas_limit}")
            return tx

        except Exception as e:
            logger.error(f"Error setting gas parameters: {str(e)}")
            tx.update({
                'gas': self.default_gas_limit,
                'gasPrice': self.w3.to_wei(self.default_gas_price_gwei, 'gwei'),
                'chainId': self.chain_id
            })
            return tx

if platform.system() == "Emscripten":
    asyncio.ensure_future(GasParams(config).set_gas_parameters(tx))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'chain_id': 1,
            'gas_limit': 200000,
            'gas_price_gwei': 50,
            'max_gas_price_gwei': 100,
            'min_gas_price_gwei': 20,
            'gas_price_samples': 10
        }
        tx = {'from': '0xYourAddress', 'to': '0xSomeAddress', 'value': 0}
        asyncio.run(GasParams(config).set_gas_parameters(tx))
