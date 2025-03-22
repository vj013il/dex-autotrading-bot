import time
from exchange_api import BinanceFIXClient  # Custom client for FIX protocol

class OrderExecutionEngine:
    def __init__(self):
        self.fix_client = BinanceFIXClient(colocation=True)  # Connecting to colocation server
        self.order_book = {}

    def on_market_data(self, data: dict):
        """Handling the glass from the exchange."""
        self.order_book = data['bids'], data['asks']
        self.adjust_orders()

    def adjust_orders(self):
        """Adjustment of orders taking into account changes in the stack."""
        best_bid = self.order_book['bids'][0][0]
        best_ask = self.order_book['asks'][0][0]
        spread = best_ask - best_bid
        
        # Placing orders at 0.1% of the best price
        self.fix_client.place_order(
            side='BUY', 
            price=best_bid * 0.999, 
            qty=100,
            execution_type='IOC'  # Immediate-Or-Cancel
        )
        self.fix_client.place_order(
            side='SELL', 
            price=best_ask * 1.001, 
            qty=100,
            execution_type='FOK'  # Fill-Or-Kill
        )
