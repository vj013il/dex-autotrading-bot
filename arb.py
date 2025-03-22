class ArbitrageEngine:
    def __init__(self):
        self.exchanges = [BinanceAPI(), CoinbaseAPI(), KrakenAPI()]

    def find_opportunities(self):
        """Searching for price imbalances."""
        prices = {}
        for exchange in self.exchanges:
            ticker = exchange.get_ticker('BTC/USDT')
            prices[exchange.name] = ticker['last_price']
        
        # Find the exchange with the minimum and maximum price
        min_exchange = min(prices, key=prices.get)
        max_exchange = max(prices, key=prices.get)
        
        if prices[max_exchange] - prices[min_exchange] > 0.002:  # spread > 0.2%
            self.execute_arbitrage(min_exchange, max_exchange)

    def execute_arbitrage(self, buy_exchange: str, sell_exchange: str):
        # Buying on a low price exchange and selling on a high price exchange
        order1 = self.exchanges[buy_exchange].buy('BTC/USDT', qty=1)
        order2 = self.exchanges[sell_exchange].sell('BTC/USDT', qty=1)
