from solders.pubkey import Pubkey

class Config:
    def __init__(self):
        self.rpc_endpoint = "https://api.mainnet-beta.solana.com"
        self.validators = ["JitoLabs", "TritonOne"]

        self.dex_list = ["Raydium", "Orca", "Serum", "Saber", "Lifinity"]
        self.dark_pools = ["SerumDarkPool"]

        self.token_a = Pubkey.from_string("So11111111111111111111111111111111111111112")  # SOL
        self.token_b = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # USDC

        self.min_profit_threshold = 0.005 
        self.max_profit_threshold = 0.015 
        self.max_slippage = 0.003 
        self.max_trade_size_percent = 0.1 
        self.capital = 100_000

        self.notify_telegram = False
        self.telegram_token = None
        self.notify_email = False
        self.email_address = None
