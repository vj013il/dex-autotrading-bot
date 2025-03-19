import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from jupiter import JupiterApi

async def execute_twap_order(
    wallet: str,
    input_mint: str,
    output_mint: str,
    total_amount: float,
    intervals: int,
    interval_seconds: int = 60
):
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    jupiter = JupiterApi(client)
    
    chunk = total_amount / intervals
    for _ in range(intervals):
        # Getting the best price
        quote = await jupiter.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=chunk,
            slippage=0.5  # 0.5%
        )
        
        # Order execution
        try:
            tx = await jupiter.swap(
                wallet_pubkey=Pubkey.from_string(wallet),
                quote_response=quote
            )
            print(f"Executed {chunk} {input_mint} -> {output_mint}")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(interval_seconds)
