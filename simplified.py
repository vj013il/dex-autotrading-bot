# Example: Basic Long/Short Futures (Margin)
class FuturesContract:
    def __init__(self, symbol, leverage, entry_price, margin):
        self.symbol = symbol          # e.g., SOL-USD
        self.leverage = leverage      # 10x
        self.entry_price = entry_price
        self.margin = margin          # Collateral
        self.position = "none"        # long/short/none

    def open_long(self, current_price):
        if self.position == "none":
            self.entry_price = current_price
            self.position = "long"
            print(f"LONG opened at {current_price} with {self.leverage}x")

    def close_position(self, current_price):
        if self.position == "long":
            pnl = (current_price - self.entry_price) * (self.margin * self.leverage)
            print(f"PNL: ${pnl:.2f}")
            self.position = "none"
