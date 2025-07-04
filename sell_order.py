from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SellOrder:
    def __init__(self, config: Dict):
        """Initialize SellOrder with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.account: LocalAccount = Account.from_key(config['private_key'])
        self.router_address = config['router_address']
        self.router_abi = json.loads(config['router_abi'])
        self.router = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
        self.token_address = config['token_address']
        self.token_abi = json.loads(config['token_abi'])
        self.token = self.w3.eth.contract(address=self.token_address, abi=self.token_abi)
        self.chain_id = config['chain_id']
        self.slippage = config['slippage']
        self.gas_limit = config['gas_limit']
        self.gas_price_gwei = config['gas_price_gwei']

    async def execute_sell(self, token_address: str, amount_in: float, min_amount_out: float) -> Optional[str]:
        """Execute a sell order for a token on a DEX."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return None

            # Approve token spending
            amount_in_wei = self.w3.to_wei(amount_in, 'ether')
            min_amount_out_wei = self.w3.to_wei(min_amount_out, 'ether')

            approve_tx = self.token.functions.approve(
                self.router_address,
                amount_in_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.to_wei(self.gas_price_gwei, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })

            signed_approve_tx = self.w3.eth.account.sign_transaction(approve_tx, self.account.key)
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
            await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, approve_tx_hash, timeout=120)

            # Build swap transaction
            path = [self.w3.to_checksum_address(token_address), self.w3.to_checksum_address(config['weth_address'])]
            deadline = int(self.w3.eth.get_block('latest')['timestamp']) + 60

            tx = self.router.functions.swapExactTokensForETH(
                amount_in_wei,
                min_amount_out_wei,
                path,
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'gas': self.gas_limit,
                'gasPrice': self.w3.to_wei(self.gas_price_gwei, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Sell order sent: {tx_hash.hex()}")

            receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash, timeout=120)
            if receipt['status'] == 1:
                logger.info(f"Sell order successful: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Sell order failed: {tx_hash.hex()}")
                return None

        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            return None

if platform.system() == "Emscripten":
    asyncio.ensure_future(SellOrder(config).execute_sell(token_address, amount_in, min_amount_out))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'private_key': 'your-private-key',
            'router_address': '0x UniswapV2Router02-address',
            'router_abi': 'uniswap-v2-router-abi.json',
            'token_address': 'token-address',
            'token_abi': 'erc20-abi.json',
            'chain_id': 1,
            'slippage': 0.05,
            'gas_limit': 200000,
            'gas_price_gwei': 50,
            'weth_address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        }
        asyncio.run(SellOrder(config).execute_sell('token-address', 1000, 0.095))
