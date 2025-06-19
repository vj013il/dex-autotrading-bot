def detect_rug_pull(transactions):
    return any(tx['value'] > 1000 for tx in transactions)
