from web3 import Web3
from utils.config import load_config
from utils.logger import Logger
from .sniping import SnipingBot

class BuyExecution(SnipingBot):
    def __init__(self):
        super().__init__()
        self.logger = Logger('buy')
        self.config = load_config()

    async def execute_buy(self, token_address, amount_in_eth):
        self.logger.info(f"Initiating buy for {token_address} with {amount_in_eth} ETH")
        try:
            amount_in = self.w3.toWei(amount_in_eth, 'ether')
            tx = self._build_swap_transaction(token_address, amount_in)
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.config['wallet']['private_key'])
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.logger.info(f"Buy successful: {tx_hash.hex()} | Status: {receipt.status}")
            return receipt
        except Exception as e:
            self.logger.error(f"Buy failed for {token_address}: {e}")
            return None
