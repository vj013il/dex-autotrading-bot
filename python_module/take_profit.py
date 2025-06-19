def apply_take_profit(current_price, entry_price, threshold=0.1):
    return current_price > entry_price * (1 + threshold)
