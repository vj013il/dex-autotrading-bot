package main

import (
    "log"
    "github.com/solana-mvp/go/mev"
)

func main() {
    client, err := mev.NewClient("Jito")
    if err != nil {
        log.Fatal(err)
    }
    err = client.ProtectTransaction("SOL/USDC", 500)
    if err != nil {
        log.Fatal(err)
    }
    log.Println("MEV-protected transaction submitted.")
}
