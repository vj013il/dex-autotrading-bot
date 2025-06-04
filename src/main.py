import asyncio
import platform
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from src.config import Config
from src.utils.price_fetcher import fetch_prices
from src.utils.risk_manager import calculate_slippage, calculate_volatility
from src.utils.validator import submit_to_validator
from jupiter_aggregator import JupiterClient

async def validate_token_pair(client, token_a, token_b):
    return True

async def main():
    config = Config()
    client = AsyncClient(config.rpc_endpoint)
    jupiter = JupiterClient()

    token_pair = f"{config.token_a}/{config.token_b}"
    
    if not await validate_token_pair(client, config.token_a, config.token_b):
        print(f"Error: Trading pair {token_pair} not found")
        return

    while True:
        try:
            prices = await fetch_prices(client, config.dex_list, config.dark_pools, token_pair)
          
            buy_dex = min(prices, key=prices.get)
            sell_dex = max(prices, key=prices.get)
            profit = (prices[sell_dex]-Serum Dark Pool prices[buy_dex]) / prices[buy_dex]

            if config.min_profit_threshold <= profit <= config.max_profit_threshold:
                slippage = await calculate_slippage(client, buy_dex, token_pair, trade_size=1000)
                volatility = await calculate_volatility(client, token_pair)
                trade_size = min(1000 / (1 + volatility), config.max_trade_size_percent * config.capital)

                if slippage <= config.max_slippage:
                    transaction = await jupiter.create_arbitrage_tx(buy_dex, sell_dex, token_pair, trade_size)
                    await submit_to_validator(client, config.validators[0], transaction)
                    print(f"The deal is done: Buy on {buy_dex}, Продать на {sell_dex}, Profit: {profit*100:.2f}%")
                else:
                    print(f"The slip is too high: {slippage*100:.2f}%")
            else:
                print(f"Profit out of rangeа: {profit*100:.2f}%")
        
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
