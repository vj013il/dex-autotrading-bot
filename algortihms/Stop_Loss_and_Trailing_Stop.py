class StopLossManager:
    def __init__(self, trigger_price: float, is_trailing: bool = False, trail_percent: float = 2.0):
        self.trigger_price = trigger_price
        self.is_trailing = is_trailing
        self.trail_percent = trail_percent
        self.best_price = 0.0
        self.active = True

    async def monitor_and_execute(self, asset: str):
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        jupiter = JupiterApi(client)
        
        while self.active:
            # Получение текущей цены
            price = await self.get_current_price(asset, client)
            
            if self.is_trailing:
                self.update_trail(price)
                
            if price <= self.trigger_price:
                await self.execute_sell_order(asset, jupiter)
                break
            
            await asyncio.sleep(10)

    def update_trail(self, current_price: float):
        if current_price > self.best_price:
            self.best_price = current_price
            self.trigger_price = current_price * (1 - self.trail_percent/100)
            print(f"Updated trail to: {self.trigger_price}")

    async def get_current_price(self, asset: str, client):
        quote = await JupiterApi(client).get_quote("SOL", "USDC", 1)
        return quote.out_amount / 1e6  # USDC decimals

    async def execute_sell_order(self, asset: str, jupiter: JupiterApi):
        # Implementation of sales logic
        print(f"Triggering sell at {self.trigger_price}")
        # ... similarly Iceberg execute
