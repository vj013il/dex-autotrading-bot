use solana_client::rpc_client::RpcClient;
use anyhow::Result;
use log::info;

pub async fn get_switchboard_price(oracle_account: &str) -> Result<f64> {
    let client = RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let account = client.get_account(&oracle_account.parse()?)?;
    let price = 100.0; // Simplified
    info!("Switchboard price for {}: {}", oracle_account, price);
    Ok(price)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    get_switchboard_price("oracle_account").await?;
    Ok(())
}
