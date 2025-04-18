from solana_mvp.twap import TWAPExecutor
from solana_mvp.dex import Orca

executor = TWAPExecutor(dex=Orca())
executor.execute_order("SOL/USDC", amount=1000)
