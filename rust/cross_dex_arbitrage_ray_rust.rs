use anchor_lang::prelude::*;
use solana_mvp::dex::{Raydium, ArbitrageEngine};

fn main() {
    let mut engine = ArbitrageEngine::new();
    engine.add_dex(Box::new(Raydium::new()));
    engine.execute_cross_dex_arbitrage();
}
