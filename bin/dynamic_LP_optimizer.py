def adjust_uniswap_v3_range(pool: UniswapPool, price: float):
    current_tick = pool.current_tick()
    lower_tick = current_tick - 100  # -1% of the current price
    upper_tick = current_tick + 100  # +1%
    pool.rebalance(lower_tick, upper_tick)
