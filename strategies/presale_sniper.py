from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PresaleSniper:
    def __init__(self, config: Dict):
        """Initialize PresaleSniper with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.account: LocalAccount = Account.from_key(config['private_key'])
        self.presale_address = config['presale_address']
        self.presale_abi = json.loads(config['presale_abi'])
        self.presale = self.w3.eth.contract(address=self.presale_address, abi=self.presale_abi)
        self.chain_id = config['chain_id']
        self.gas_limit = config['gas_limit']
        self.max_gas_price_gwei = config.get('max_gas_price_gwei', 100)

    async def snipe_presale(self, amount_in: float, token_address: str) -> Optional[str]:
        """Snipe a presale by monitoring and participating when available."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return None

            # Check if presale is active
            is_active = await asyncio.to_thread(self.presale.functions.isPresaleActive().call)
            if not is_active:
                logger.info("Presale not active, waiting...")
                while not await asyncio.to_thread(self.presale.functions.isPresaleActive().call):
                    await asyncio.sleep(0.1)  # Check every 100ms

            # Run security checks
            security = SecurityChecks(config)
            if await security.check_honeypot(token_address) or await security.check_rug_pull(token_address, self.presale_address):
                logger.error(f"Token {token_address} failed security checks")
                return None

            # Apply anti-bot bypass
            anti_bot_params = await security.bypass_anti_bot(token_address)
            amount_in_wei = self.w3.to_wei(amount_in, 'ether')

            # Build participation transaction
            tx = self.presale.functions.participate().build_transaction({
                'from': self.account.address,
                'value': amount_in_wei,
                'gas': self.gas_limit,
                'gasPrice': anti_bot_params['gasPrice'],
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Presale snipe sent: {tx_hash.hex()}")

            receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash, timeout=120)
            if receipt['status'] == 1:
                logger.info(f"Presale snipe successful: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Presale snipe failed: {tx_hash.hex()}")
                return None

        except Exception as e:
            logger.error(f"Error sniping presale for {token_address}: {str(e)}")
            return None

if platform.system() == "Emscripten":
    asyncio.ensure_future(PresaleSniper(config).snipe_presale(amount_in, token_address))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'private_key': 'your-private-key',
            'presale_address': '0xPresaleContractAddress',
            'presale_abi': '{"abi": [{"inputs":[],"name":"participate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"isPresaleActive","outputs":[{"name":"","type":"bool"}],"stateMutability":"view","type":"function"}]}',
            'token_abi': 'erc20_abi.json',
            'router_abi': 'uniswap_v2_router_abi.json',
            'pair_abi': 'uniswap_v2_pair_abi.json',
            'chain_id': 1,
            'gas_limit': 200000,
            'max_gas_price_gwei': 100
        }
        asyncio.run(PresaleSniper(config).snipe_presale(0.1, 'token-address'))
