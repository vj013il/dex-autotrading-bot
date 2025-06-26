from web3 import Web3
from utils.config import load_config

class SellTransaction:
    def __init__(self):
        self.config = load_config()
        self.w3 = Web3(Web3.WebsocketProvider(self.config['rpc_url']))
        self.account = self.w3.eth.account.from_key(self.config['private_key'])

    def execute_sell(self, token_address, amount, slippage=5, take_profit=10):
        """Execute a sell transaction with stop-loss and take-profit triggers."""
        contract = self.w3.eth.contract(address=self.config['router_address'], abi=self.config['router_abi'])
        amount_in = Web3.to_wei(amount, 'ether')
        amount_out_min = int(amount * (100 - slippage) / 100)

        # Check take-profit condition
        current_price = self.get_current_price(token_address)
        if current_price >= take_profit * self.get_entry_price(token_address):
            tx = contract.functions.swapExactTokensForETH(
                amount_in,
                amount_out_min,
                [token_address, self.config['weth_address']],
                self.account.address,
                int(time.time()) + 600
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': Web3.to_wei('50', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.config['private_key'])
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Sell transaction sent: {tx_hash.hex()}")
            return tx_hash
        return None

    def get_current_price(self, token_address):
        """Placeholder for fetching current token price."""
        return 100  # Mock price in USD

    def get_entry_price(self, token_address):
        """Placeholder for fetching entry price."""
        return 80  # Mock entry price in USD
