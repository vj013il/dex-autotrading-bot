import requests

class DexManager:
    def __init__(self, dex_api_urls):
        self.dex_apis = dex_api_urls  # e.g., {'raydium': 'https://api.raydium.io/v2'}

    def place_order(self, dex_name, order_params):
        response = requests.post(
            f"{self.dex_apis[dex_name]}/order",
            json=order_params
        )
        return response.json()

    def arbitrage_check(self, token_pair):
        prices = {}
        for dex, url in self.dex_apis.items():
            res = requests.get(f"{url}/price?pair={token_pair}")
            prices[dex] = res.json()['price']
        return max(prices, key=prices.get)  # Пул с максимальной ценой
