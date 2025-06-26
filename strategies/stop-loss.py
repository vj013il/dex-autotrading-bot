from web3 import Web3
from utils.config import load_config

class StopLoss:
    def __init__(self):
        self.config = load_config()
        self.w3 = Web3(Web3.WebsocketProvider(self.config['rpc_url']))

    def monitor_stop_loss(self, token_address, stop_loss_price):
        """Monitor price and trigger stop-loss if price falls below threshold."""
        current_price = self.get_current_price(token_address)
        if current_price <= stop_loss_price:
            print(f"Stop-loss triggered for {token_address} at {current_price}")
            # Trigger sell transaction
            from core.sell import SellTransaction
            sell = SellTransaction()
            sell.execute_sell(token_address, 1.0, slippage=5, take_profit=0)
        else:
            print(f"Price {current_price} above stop-loss {stop_loss_price}")

    def get_current_price(self, token_address):
        """Placeholder for fetching current token price."""
        return 90  # Mock price in USD
