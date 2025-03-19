import asyncio
from solana.rpc.async_api import AsyncClient
from jupiter import JupiterApi

class IcebergOrder:
    def __init__(self, total_amount: float, chunk_size: float, interval: int):
        self.total_amount = total_amount
        self.chunk_size = chunk_size
        self.interval = interval
        self.remaining = total_amount
        self.is_running = False

    async def execute(self, input_mint: str, output_mint: str, wallet: str):
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        jupiter = JupiterApi(client)
        self.is_running = True
        
        while self.remaining > 0 and self.is_running:
            current_chunk = min(self.chunk_size, self.remaining)
            
            try:
                # Obtaining a quote
                quote = await jupiter.get_quote(
                    input_mint=input_mint,
                    output_mint=output_mint,
                    amount=current_chunk,
                    slippage=0.5
                )
                
                # Order execution
                tx = await jupiter.swap(
                    wallet_pubkey=wallet,
                    quote_response=quote
                )
                print(f"Executed {current_chunk} {input_mint}")
                self.remaining -= current_chunk
                
            except Exception as e:
                print(f"Error: {e}")
            
            await asyncio.sleep(self.interval)
        
        print("Iceberg order completed")

# Utilization
order = IcebergOrder(total_amount=1000, chunk_size=100, interval=60)
asyncio.run(order.execute("USDC", "SOL", "YOUR_WALLET_ADDRESS"))
