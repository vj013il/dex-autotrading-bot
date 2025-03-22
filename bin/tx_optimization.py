def optimize_fee(exchange: str, volume: float) -> float:
    tier = exchange.get_fee_tier(volume)
    maker_fee = tier['maker']
    taker_fee = tier['taker']
    # Choice between maker/taker depending on strategy
    return maker_fee if volume > 1e6 else taker_fee
