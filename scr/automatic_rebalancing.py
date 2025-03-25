import schedule
import time

class Rebalancer:
    def __init__(self, oracle_client):
        self.oracle = oracle_client

    def time_based_rebalance(self, interval_minutes):
        schedule.every(interval_minutes).minutes.do(self.execute_rebalance)

    def price_based_rebalance(self, target_price, threshold_percent):
        current_price = self.oracle.get_price()
        if abs(current_price - target_price) / target_price > threshold_percent:
            self.execute_rebalance()

    def execute_rebalance(self):
        # Order repositioning logic
        pass
