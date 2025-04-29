use crate::core::{solana_client::SolanaClient, jito_client::JitoClient};
use anyhow::Result;
use log::info;

mod core;
mod strategies;
mod integrations;
mod monitoring;
mod utils;

#[tokio::main]
async fn main() -> Result<()> {
    utils::logger::init_logger();
    let solana_client = SolanaClient::new("https://api.mainnet-beta.solana.com")?;
    let jito_client = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    info!("Solana PulseTrader with Jito support initialized");
    // Start strategies
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    Ok(())
}
