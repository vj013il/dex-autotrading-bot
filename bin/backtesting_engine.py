class Backtester:
    def run(self, strategy, historical_data):
        for candle in historical_data:
            strategy.on_candle(candle)
            pnl = self.calculate_pnl(strategy.positions)
            if pnl < -self.max_drawdown:
                break
        return strategy.performance_metrics()
