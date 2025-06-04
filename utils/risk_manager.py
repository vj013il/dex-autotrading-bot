import numpy as np

async def calculate_slippage(client, platform, token_pair, trade_size):
    return 0.002 

async def calculate_volatility(client, token_pair, blocks=100):
    price_history = await get_price_history(client, token_pair, blocks)
    return np.std(price_history)

async def get_price_history(client, token_pair, blocks):
    return [100 + i * 0.1 for i in range(blocks)]
