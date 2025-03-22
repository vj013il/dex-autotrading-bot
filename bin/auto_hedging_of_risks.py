def auto_hedge(position: float):
    futures_exchange = Bybit()
    spot_exposure = get_spot_exposure()
    if spot_exposure > 0:
        futures_exchange.short(spot_exposure)
    elif spot_exposure < 0:
        futures_exchange.long(-spot_exposure)
