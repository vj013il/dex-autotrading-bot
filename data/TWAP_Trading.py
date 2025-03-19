import asyncio
from solana.rpc.async_api import AsyncClient
from jupiter import JupiterApi

async def execute_twap_order(
    wallet: str, 
    input_token: str, 
    output_token: str, 
    total_amount: float, 
    intervals: int
):
    client = AsyncClient("https://ssc-dao.genesysgo.net")
    jupiter = JupiterApi(client)
    
    chunk = total_amount / intervals
    for _ in range(intervals):
        quote = await jupiter.get_quote(input_token, output_token, chunk)
        tx = await jupiter.swap(wallet, quote)
        print(f"Executed chunk: {tx}")
        await asyncio.sleep(60)  # 1 мин между ордерами

# Пример вызова
asyncio.run(execute_twap_order(
    wallet="YOUR_WALLET_ADDRESS",
    input_token="USDC",
    output_token="SOL",
    total_amount=100000,  # $100k
    intervals=100
))
