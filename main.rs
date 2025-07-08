use crate::arbitrage::Arbitrage;
use crate::config::Config;
use crate::exchange::{CexClient, DexClient};
use solana_client::rpc_client::RpcClient;
use solana_sdk::pubkey::Pubkey;
use std::error::Error;
use tokio::time::{interval, Duration};
use log::{error, info};

mod arbitrage;
mod config;
mod exchange;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    env_logger::init();

    // Load configuration
    let config = Config::load("config.json")?;
    let solana_rpc = RpcClient::new(config.solana_rpc_url.clone());

    // Initialize CEX and DEX clients
    let cex_client = CexClient::new(&config.cex_api_keys, &config.exchanges);
    let dex_client = DexClient::new(&solana_rpc, &config.dex_config);

    // Initialize arbitrage engine
    let mut arbitrage = Arbitrage::new(config, cex_client, dex_client);

    // Run Python price monitor (via subprocess)
    let python_monitor = std::process::Command::new("python3")
        .arg("python/monitor.py")
        .spawn()?;

    // Main loop
    let mut interval = interval(Duration::from_millis((config.check_interval * 1000.0) as u64));
    loop {
        interval.tick().await;
        match arbitrage.find_and_execute_opportunities().await {
            Ok(_) => info!("Arbitrage cycle completed"),
            Err(e) => error!("Error in arbitrage cycle: {}", e),
        }
    }
}
