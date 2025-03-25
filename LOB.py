# Simplified Order Book (Bids/Asks)
class OrderBook:
    def __init__(self):
        self.bids = {}  # Format: {price: quantity}
        self.asks = {}

    def add_order(self, price, quantity, side):
        if side == "bid":
            self.bids[price] = self.bids.get(price, 0) + quantity
        elif side == "ask":
            self.asks[price] = self.asks.get(price, 0) + quantity

    def best_bid_ask(self):
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return best_bid, best_ask
