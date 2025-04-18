{-# LANGUAGE OverloadedStrings #-}
module Main where

import SolanaMVP
import Dex.Meteora

main :: IO ()
main = do
    client <- initClient "Meteora"
    let strat = FlashLoanArbitrage client
    executeFlashLoan strat "SOL" "USDC" 10000
    putStrLn "Flash loan arbitrage executed."
