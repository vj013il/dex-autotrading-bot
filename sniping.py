import asyncio
from web3 import Web3
from utils.config import load_config
from utils.logger import Logger
from utils.security import SecurityScanner

class SnipingBot:
    def __init__(self):
        self.config = load_config()
        self.w3 = Web3(Web3.WebsocketProvider(self.config['nodes']['private_node']))
        self.logger = Logger('sniping')
        self.security = SecurityScanner()
        self.dex_contracts = self.config['dexs']
        self.account = self.w3.eth.account.from_key(self.config['wallet']['private_key'])

    async def monitor_mempool(self):
        self.logger.info("Starting mempool monitoring for: " + self.account.address)
        while True:
            try:
                pending_txs = self.w3.eth.filter('pending').get_new_entries()
                for tx in pending_txs:
                    if self._is_token_pair_tx(tx, self.dex_contracts):
                        await self._snipe_token(tx['token_address'])
            except Exception as e:
                self.logger.error(f"Mempool monitoring error: {e}")
            await asyncio.sleep(0.002)  # 2ms polling interval

    async def _snipe_token(self, token_address):
        if not self.security.scan_contract(token_address):
            self.logger.warning(f"Contract {token_address} failed security check")
            return

        try:
            amount_in = self.w3.toWei(self.config['snipe_amount'], 'ether')
            tx = self._build_swap_transaction(token_address, amount_in)
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.logger.info(f"Sniped token {token_address} with tx: {tx_hash.hex()}")
        except Exception as e:
            self.logger.error(f"Sniping failed for {token_address}: {e}")

    def _build_swap_transaction(self, token_address, amount_in):
        # Placeholder for swap logic (e.g., Uniswap V3)
        return {
            'from': self.account.address,
            'to': self.dex_contracts['uniswap_v3']['router'],
            'value': amount_in,
            'gas': 300000,
            'gasPrice': self.w3.toWei(50, 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'data': '0x{...}'  # Simplified swap data
        }

    def _is_token_pair_tx(self, tx, contracts):
        # Simplified check for token pair transactions
        return tx.get('to') in contracts.values() and 'methodId' in tx

if __name__ == "__main__":
    bot = SnipingBot()
    asyncio.run(bot.monitor_mempool())
