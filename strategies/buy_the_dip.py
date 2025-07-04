from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuyTheDip:
    def __init__(self, config: Dict):
        """Initialize BuyTheDip with configuration."""
        self.w3 = Web3(Web3.WebsocketProvider(config['node_url']))
        self.account: LocalAccount = Account.from_key(config['private_key'])
        self.router_address = config['router_address']
        self.router_abi = json.loads(config['router_abi'])
        self.router = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
        self.chain_id = config['chain_id']
        self.slippage = config['slippage']
        self.gas_limit = config['gas_limit']

    async def monitor_and_buy_dip(self, token_address: str, amount_in: float, dip_threshold: float) -> Optional[str]:
        """Monitor price and buy when it dips below the threshold."""
        try:
            if not self.w3.is_connected():
                logger.error("Not connected to node")
                return None

            pair_address = self.router.functions.getPair(
                self.w3.to_checksum_address(token_address),
                self.w3.to_checksum_address(config['weth_address'])
            ).call()
            pair_abi = json.loads(config['pair_abi'])
            pair = self.w3.eth.contract(address=pair_address, abi=pair_abi)

            # Monitor price
            initial_price = None
            while True:
                reserves = await asyncio.to_thread(pair.functions.getReserves().call)
                current_price = reserves[1] / reserves[0]  # Simplified price calculation
                if initial_price is None:
                    initial_price = current_price
                    logger.info(f"Initial price set: {initial_price}")
                    continue

                price_drop = (initial_price - current_price) / initial_price
                if price_drop >= dip_threshold:
                    logger.info(f"Dip detected: {price_drop*100}% drop, buying...")

                    # Run security checks
                    security = SecurityChecks(config)
                    if await security.check_honeypot(token_address) or await security.check_rug_pull(token_address, pair_address):
                        logger.error(f"Token {token_address} failed security checks")
                        return None

                    # Apply anti-bot bypass
                    anti_bot_params = await security.bypass_anti_bot(token_address)
                    amount_in_wei = self.w3.to_wei(amount_in, 'ether')
                    min_amount_out_wei = self.w3.to_wei(amount_in * current_price * (1 - self.slippage), 'ether')

                    # Build buy transaction
                    path = [self.w3.to_checksum_address(config['weth_address']), self.w3.to_checksum_address(token_address)]
                    deadline = int(self.w3.eth.get_block('latest')['timestamp']) + 60

                    tx = self.router.functions.swapExactETHForTokens(
                        min_amount_out_wei,
                        path,
                        self.account.address,
                        deadline
                    ).build_transaction({
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
                    logger.info(f"Buy-the-dip order sent: {tx_hash.hex()}")

                    receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash, timeout=120)
                    if receipt['status'] == 1:
                        logger.info(f"Buy-the-dip successful: {tx_hash.hex()}")
                        return tx_hash.hex()
                    else:
                        logger.error(f"Buy-the-dip failed: {tx_hash.hex()}")
                        return None

                await asyncio.sleep(1)  # Check every second

        except Exception as e:
            logger.error(f"Error executing buy-the-dip for {token_address}: {str(e)}")
            return None

if platform.system() == "Emscripten":
    asyncio.ensure_future(BuyTheDip(config).monitor_and_buy_dip(token_address, amount_in, dip_threshold))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'private_key': 'your-private-key',
            'router_address': '0xUniswapV2Router02-address',
            'router_abi': 'uniswap_v2_router_abi.json',
            'pair_abi': 'uniswap_v2_pair_abi.json',
            'token_abi': 'erc20_abi.json',
            'chain_id': 1,
            'slippage': 0.05,
            'gas_limit': 200000,
            'weth_address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        }
        asyncio.run(BuyTheDip(config).monitor_and_buy_dip('token-address', 0.1, 0.1))  # 10% dip threshold
