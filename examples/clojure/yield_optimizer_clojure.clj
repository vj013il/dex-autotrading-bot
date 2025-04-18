(ns solana-mvp.yield-optimizer
  (:require [solana-mvp.dex :refer [OrcaClient]]
            [solana-mvp.strategy :refer [LiquidityMiningOptimizer]]))

(defn -main []
  (let [client (OrcaClient.)
        optimizer (LiquidityMiningOptimizer. client)]
    (-> optimizer
        (.find-opportunities ["SOL/USDC" "wSOL/USDC"])
        (.execute))))
