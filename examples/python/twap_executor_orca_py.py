#!/usr/bin/env python3
from solana_mvp.twap import TWAPExecutor
from solana_mvp.dex import Orca

def main():
    executor = TWAPExecutor(dex=Orca())
    executor.execute_order("SOL/USDC", amount=1000, slices=10)

if __name__ == "__main__":
    main()
