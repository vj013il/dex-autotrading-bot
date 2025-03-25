import time
from typing import List, Dict

class RiskManager:
    def __init__(self, total_capital: float):
        self.total_capital = total_capital
        self.pool_volume_history: Dict[str, List[float]] = {}  # {pool_id: [volume_0, volume_1h]}
        self.blacklist = ["TOKEN_ADDR1", "TOKEN_ADDR2"]  # Example of a blacklist

    def check_order_size(self, order_amount: float) -> bool:
        """Verification that the order does not exceed 5% of capital"""
        max_allowed = self.total_capital * 0.05
        return order_amount <= max_allowed

    def update_pool_volume(self, pool_id: str, current_volume: float):
        """Updating pool volume data"""
        if pool_id not in self.pool_volume_history:
            self.pool_volume_history[pool_id] = []
        self.pool_volume_history[pool_id].append(current_volume)
        # Storing data for the last hour
        if len(self.pool_volume_history[pool_id]) > 60:
            self.pool_volume_history[pool_id].pop(0)

    def check_stop_loss(self, pool_id: str, threshold: float) -> bool:
        """Stop loss activation at X% volume loss"""
        history = self.pool_volume_history.get(pool_id, [])
        if len(history) < 2:
            return False
        change = (history[-1] - history[0]) / history[0]
        return change <= -threshold  # For example, -0.3 for 30%

    def is_token_allowed(self, token_address: str, current_volume: float) -> bool:
        """Blacklisting token verification"""
        return (
            token_address not in self.blacklist
            and current_volume >= 1_000_000  # $1M
            and self.is_contract_verified(token_address)
        )

    def is_contract_verified(self, token_address: str) -> bool:
        """Contract verification check (stub)"""
        # Real implementation via Solscan API or analogs
        return token_address.startswith("V")
