class RiskManager:
    def __init__(self):
        self.max_drawdown = -0.05  # max. drawdown (-5%)
        self.position_limits = {'BTC': 1000}  # position limit in BTC

    def check_limits(self, current_pnl: float, positions: dict) -> bool:
        """Limit check."""
        if current_pnl < self.max_drawdown:
            self.trigger_emergency_stop()
            return False
        
        for asset, limit in self.position_limits.items():
            if positions.get(asset, 0) > limit:
                self.cancel_all_orders(asset)
                return False
        return True
