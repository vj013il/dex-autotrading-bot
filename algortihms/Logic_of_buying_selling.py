class TradingEngine:
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")
        self.jupiter = JupiterApi(self.client)

    async def market_buy(self, input_mint: str, output_mint: str, amount: float):
        quote = await self.jupiter.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage=0.5
        )
        return await self.jupiter.swap(
            wallet_pubkey=self.wallet,
            quote_response=quote
        )

    async def market_sell(self, input_mint: str, output_mint: str, amount: float):
        return await self.market_buy(output_mint, input_mint, amount)

    async def limit_order(self, price: float, amount: float):
        # Limit orders require integration with a DEX that supports them (e.g. OpenBook)
        pass
