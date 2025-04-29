use solana_client::rpc_client::RpcClient;
use anyhow::Result;
use log::{info, warn};

pub async fn check_program_risk(program_id: &str, min_lamports: u64) -> Result<bool> {
    let client = RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let accounts = client.get_program_accounts(&program_id.parse()?)?;
    if accounts.iter().any(|acc| acc.lamports < min_lamports) {
        warn!("Risky program detected: {}", program_id);
        Ok(true)
    } else {
        info!("Program {} appears safe", program_id);
        Ok(false)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    check_program_risk("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", 1000).await?;
    Ok(())
}
