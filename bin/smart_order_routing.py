def smart_order_router(symbol: str, quantity: float) -> str:
    exchanges = [Binance, Coinbase, Kraken]
    costs = []
    for exchange in exchanges:
        fee = exchange.get_taker_fee(symbol)
        price = exchange.get_price(symbol)
        cost = quantity * price * (1 + fee)
        costs.append((exchange.name, cost))
    return min(costs, key=lambda x: x[1])[0]  # Selecting an exchange with min. cost
