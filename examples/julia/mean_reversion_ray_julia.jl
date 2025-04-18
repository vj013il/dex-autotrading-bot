using SolanaMVP, Raydium

client = Raydium.Client()
strategy = MeanReversionStrategy(client; window=20, threshold=0.01)
run_strategy(strategy, "SOL/USDC", 1000)
