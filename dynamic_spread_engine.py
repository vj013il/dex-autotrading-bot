class SpreadEngine:
    def __init__(self):
        self.volatility_window = 20  # volatility period (in seconds)
        self.min_spread = 0.0001  # min. spread (0.01%)

    def calculate_spread(self, historical_prices: list) -> float:
        """Spread calculation based on volatility."""
        returns = [historical_prices[i]/historical_prices[i-1] - 1 for i in range(1, len(historical_prices))]
        volatility = np.std(returns) * np.sqrt(365 * 24 * 3600)  # annual volatility
        
        # Formula: spread = volatility * coefficient + minimum spread
        dynamic_spread = volatility * 0.5 + self.min_spread
        return max(dynamic_spread, self.min_spread)
