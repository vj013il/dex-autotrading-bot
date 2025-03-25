# Spread setting
class SpreadManager:
    def __init__(self, spread_type='fixed', volatility_coeff=0.1):
        self.spread_type = spread_type
        self.coeff = volatility_coeff

    def get_spread(self, current_price, volatility_24h=None):
        if self.spread_type == 'fixed':
            return current_price * 0.005  # 0.5%
        elif self.spread_type == 'dynamic':
            return volatility_24h * self.coeff * current_price

# Strategy templates
STRATEGY_TEMPLATES = {
    "stable": {"spread": "fixed", "order_dist": "uniform"},
    "volatile": {"spread": "dynamic", "order_dist": "logarithmic"}
}

# Order allocation
class OrderDistributor:
    def distribute_orders(self, mid_price, spread, num_orders=10, mode='uniform'):
        price_levels = []
        if mode == 'uniform':
            step = spread * 2 / num_orders
            price_levels = [mid_price - spread + i*step for i in range(num_orders)]
        elif mode == 'logarithmic':
            # Logarithmic distribution
            pass
        return price_levels
