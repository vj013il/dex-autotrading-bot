from datetime import datetime, timedelta

class FraudDetector:
    def __init__(self):
        self.transaction_history = {}
    
    def log_transaction(self, wallet: str, amount: float, token: str):
        now = datetime.now()
        if wallet not in self.transaction_history:
            self.transaction_history[wallet] = []
        
        self.transaction_history[wallet].append({
            "time": now,
            "amount": amount,
            "token": token
        })
    
    def check_suspicious_activity(self, wallet: str):
        transactions = self.transaction_history.get(wallet, [])
        if len(transactions) == 0:
            return False
        
        # Checking for large transactions (> $1M)
        large_tx = any(tx["amount"] > 1_000_000 for tx in transactions)
        
        # Checking for frequent transactions (> 10/минуту)
        recent_tx = [tx for tx in transactions if tx["time"] > datetime.now() - timedelta(minutes=1)]
        high_frequency = len(recent_tx) > 10
        
        return large_tx or high_frequency
