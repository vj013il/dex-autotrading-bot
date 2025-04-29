use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn farm_saber_pool(farm_id: &str, amount: f64) -> Result<String> {
    let program_id = Pubkey::from_str("SabER1gLji4A5KXgQVoCZMhD5NULjKDsy3PBER1V3t4")?;
    let tx = Transaction::new_with_payer(&[/* stake instruction */], None);
    let client = solana_client::rpc_client::RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let signature = client.send_and_confirm_transaction(&tx)?;
    info!("Staked in Saber farm {}: {}", farm_id, signature);
    Ok(signature.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    farm_saber_pool("farm_id", 100.0).await?;
    Ok(())
}
