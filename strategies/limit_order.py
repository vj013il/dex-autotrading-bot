from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LimitOrder:
    def __init__(self, config: Dict):
        """Initialize LimitOrder with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.account: LocalAccount = Account.from_key(config['private_key'])
        self.router_address = config['router_address']
        self.router_abi = json.loads(config['router_abi'])
        self.router = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
        self.chain_id = config['chain_id']
        self.gas_limit = config['gas_limit']
        self.gas_price_gwei = config['gas_price_gwei']

    async def place_limit_order(self, token_address: str, amount_in: float, target_price: float, is_buy: bool) -> Optional[str]:
        """Place a limit order for a token at a specific price."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return None

            # Get current price from DEX (simplified, assumes Uniswap-like pair)
            pair_address = self.router.functions.getPair(
                self.w3.to_checksum_address(token_address),
                self.w3.to_checksum_address(config['weth_address'])
            ).call()
            pair_abi = json.loads(config['pair_abi'])
            pair = self.w3.eth.contract(address=pair_address, abi=pair_abi)
            reserves = pair.functions.getReserves().call()
            current_price = reserves[1] / reserves[0]  # Simplified price calculation

            if (is_buy and current_price <= target_price) or (not is_buy and current_price >= target_price):
                amount_in_wei = self.w3.to_wei(amount_in, 'ether')
                min_amount_out_wei = self.w3.to_wei(amount_in * target_price * (1 - config['slippage']), 'ether')
                path = [self.w3.to_checksum_address(config['weth_address']), self.w3.to_checksum_address(token_address)] if is_buy else \
                       [self.w3.to_checksum_address(token_address), self.w3.to_checksum_address(config['weth_address'])]
                deadline = int(self.w3.eth.get_block('latest')['timestamp']) + 60

                # Approve tokens for sell order
                if not is_buy:
                    token = self.w3.eth.contract(address=token_address, abi=json.loads(config['token_abi']))
                    approve_tx = token.functions.approve(
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
                tx_func = self.router.functions.swapExactETHForTokens if is_buy else self.router.functions.swapExactTokensForETH
                tx = tx_func(
                    min_amount_out_wei,
                    path,
                    self.account.address,
                    deadline
                ).build_transaction({
                    'from': self.account.address,
                    'value': amount_in_wei if is_buy else 0,
                    'gas': self.gas_limit,
                    'gasPrice': self.w3.to_wei(self.gas_price_gwei, 'gwei'),
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'chainId': self.chain_id
                })

                # Sign and send transaction
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                logger.info(f"Limit order sent: {tx_hash.hex()}")

                receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash, timeout=120)
                if receipt['status'] == 1:
                    logger.info(f"Limit order successful: {tx_hash.hex()}")
                    return tx_hash.hex()
                else:
                    logger.error(f"Limit order failed: {tx_hash.hex()}")
                    return None
            else:
                logger.info("Price condition not met for limit order")
                return None

        except Exception as e:
            logger.error(f"Error executing limit order: {str(e)}")
            return None

if platform.system() == "Emscripten":
    asyncio.ensure_future(LimitOrder(config).place_limit_order(token_address, amount_in, target_price, is_buy))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'private_key': 'your-private-key',
            'router_address': '0x UniswapV2Router02-address',
            'router_abi': 'uniswap-v2-router-abi.json',
            'token_abi': 'erc20-abi.json',
            'pair_abi': 'uniswap-v2-pair-abi.json',
            'chain_id': 1,
            'slippage': 0.05,
            'gas_limit': 200000,
            'gas_price_gwei': 50,
            'weth_address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        }
        asyncio.run(LimitOrder(config).place_limit_order('token-address', 0.1, 0.0001, True))
