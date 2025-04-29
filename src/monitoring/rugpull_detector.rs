use solana_client::rpc_client::RpcClient;
use anyhow::Result;
use log::{info, warn};

pub async fn detect_rugpull(token_mint: &str, min_liquidity: u64) -> Result<bool> {
    let client = RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let balance = client.get_token_account_balance(&token_mint.parse()?)?;
    if balance.ui_amount.unwrap_or(0.0) as u64 <= min_liquidity {
        warn!("Rugpull detected for {}: Low liquidity", token_mint);
        Ok(true)
    } else {
        info!("No rugpull detected for {}", token_mint);
        Ok(false)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    detect_rugpull("token_mint", 1000).await?;
    Ok(())
}
