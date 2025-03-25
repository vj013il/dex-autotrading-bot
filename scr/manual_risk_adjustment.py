class RiskManager:
    def __init__(self, max_order_percent=5, blacklist=[]):
        self.max_order_percent = max_order_percent
        self.blacklist = blacklist  # List of tokens

    def check_order(self, token, order_amount, total_capital):
        if token in self.blacklist:
            return False
        if order_amount > total_capital * (self.max_order_percent / 100):
            return False
        return True

    def stop_loss_check(self, pool_volume_history):
        hour_volume_change = (pool_volume_history[-1] - pool_volume_history[0]) / pool_volume_history[0]
        return hour_volume_change < -0.3  # -30%
