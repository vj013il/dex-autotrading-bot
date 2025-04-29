use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::Result;
use log::info;

#[derive(Serialize, Deserialize)]
pub struct Trade {
    pub amount: f64,
    pub tx_id: String,
}

pub struct MEVOpportunityMonitor;

impl MEVOpportunityMonitor {
    pub fn new() -> Self {
        Self
    }

    pub async fn detect_large_trade(&self, token_mint: &str) -> Result<Option<Trade>> {
        let client = Client::new();
        let txs: Vec<Trade> = client.get(format!("https://api.solana.fm/transactions/{}", token_mint))
            .send()
            .await?
            .json()
            .await?;
        for tx in txs {
            if tx.amount > 100.0 {
                info!("Large trade detected for {}: {}", token_mint, tx.amount);
                return Ok(Some(tx));
            }
        }
        Ok(None)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let monitor = MEVOpportunityMonitor::new();
    monitor.detect_large_trade("SOL").await?;
    Ok(())
}
