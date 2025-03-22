def sync_prices(symbol: str):
    cefi_price = binance.get_price(symbol)
    defi_price = uniswap.get_price(symbol)
    if abs(cefi_price - defi_price) > 0.005:
        execute_hedge(cefi_price, defi_price)
