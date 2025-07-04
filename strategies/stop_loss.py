from web3 import Web3
import json
import asyncio
import logging
from typing import Dict, Optional
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StopLoss:
    def __init__(self, config: Dict):
        """Initialize StopLoss with configuration."""
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

    async def set_stop_loss(self, token_address: str, amount: float, stop_price: float) -> Optional[str]:
        """Monitor price and execute a sell order if stop price is reached."""
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

            # Monitor price in a loop
            while True:
                reserves = pair.functions.getReserves().call()
                current_price = reserves[1] / reserves[0]  # Simplified price calculation
                if current_price <= stop_price:
                    logger.info(f"Stop loss triggered at price: {current_price}")
                    amount_in_wei = self.w3.to_wei(amount, 'ether')
                    min_amount_out_wei = self.w3.to_wei(amount * stop_price * (1 - self.slippage), 'ether')

                    # Approve token spending
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

                    # Execute sell
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

                    signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    logger.info(f"Stop loss sell order sent: {tx_hash.hex()}")

                    receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash, timeout=120)
                    if receipt['status'] == 1:
                        logger.info(f"Stop loss sell order successful: {tx_hash.hex()}")
                        return tx_hash.hex()
                    else:
                        logger.error(f"Stop loss sell order failed: {tx_hash.hex()}")
                        return None
                await asyncio.sleep(1)  # Check every second

        except Exception as e:
            logger.error(f"Error executing stop loss: {str(e)}")
            return None

if platform.system() == "Emscripten":
    asyncio.ensure_future(StopLoss(config).set_stop_loss(token_address, amount, stop_price))
else:
    if __name__ == "__main__":
        config = {
            'node_url': 'wss://your-private-node-url',
            'private_key': 'your-private-key',
            'router_address': '0x UniswapV2Router02-address',
            'router_abi': 'uniswap-v2-router-abi.json',
            'token_address': 'token-address',
            'token_abi': 'erc20-abi.json',
            'pair_abi': 'uniswap-v2-pair-abi.json',
            'chain_id': 1,
            'slippage': 0.05,
            'gas_limit': 200000,
            'gas_price_gwei': 50,
            'weth_address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        }
        asyncio.run(StopLoss(config).set_stop_loss('token-address', 1000, 0.00008))
