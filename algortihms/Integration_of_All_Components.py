async def main():
    wallet = "YOUR_WALLET_ADDRESS"
    
    # Engine initialization
    trader = TradingEngine(wallet)
    
    # Iceberg buying SOL in $1000 increments of $100
    iceberg = IcebergOrder(1000, 100, 60)
    asyncio.create_task(iceberg.execute("USDC", "SOL", wallet))
    
    # Setting a trailing stop loss 5% below the high
    stop_loss = StopLossManager(0, is_trailing=True, trail_percent=5)
    asyncio.create_task(stop_loss.monitor_and_execute("SOL"))
    
    # Example of a manual sale
    await asyncio.sleep(3600)  # After 1 hour
    await trader.market_sell("SOL", "USDC", 10)  # Sale 10 SOL

asyncio.run(main())
