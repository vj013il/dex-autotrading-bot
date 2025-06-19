def apply_stop_loss(current_price, entry_price, threshold=0.05):
    return current_price < entry_price * (1 - threshold)
