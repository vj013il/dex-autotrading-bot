import json
from typing import Dict, List

class Config:
    def __init__(self, exchanges: List[str], pairs: List[str], min_spread: float, max_order_size: float,
                 min_profit_usd: float, cex_api_keys: Dict[str, Dict], dex_config: Dict[str, str],
                 check_interval: float, max_slippage: float, solana_rpc_url: str):
        self.exchanges = exchanges
        self.pairs = pairs
        self.min_spread = min_spread
        self.max_order_size = max_order_size
        self.min_profit_usd = min_profit_usd
        self.cex_api_keys = cex_api_keys
        self.dex_config = dex_config
        self.check_interval = check_interval
        self.max_slippage = max_slippage
        self.solana_rpc_url = solana_rpc_url

    @staticmethod
    def load(path: str) -> 'Config':
        with open(path, 'r') as f:
            data = json.load(f)
        return Config(
            exchanges=data['exchanges'],
            pairs=data['pairs'],
            min_spread=data['min_spread'],
            max_order_size=data['max_order_size'],
            min_profit_usd=data['min_profit_usd'],
            cex_api_keys=data['cex_api_keys'],
            dex_config=data['dex_config'],
            check_interval=data['check_interval'],
            max_slippage=data['max_slippage'],
            solana_rpc_url=data['solana_rpc_url']
        )

if __name__ == "__main__":
    config = Config.load('config.json')
    print(config.__dict__)
