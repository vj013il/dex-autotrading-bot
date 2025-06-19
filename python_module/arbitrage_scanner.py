def scan_arbitrage(prices):
    opportunities = []
    for dex1, dex2 in itertools.combinations(prices, 2):
        if abs(dex1['price'] - dex2['price']) > 0.01:
            opportunities.append((dex1, dex2))
    return opportunities
