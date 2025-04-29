use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use crate::core::{jito_client::JitoClient, transaction_optimizer};
use anyhow::Result;
use log::info;

pub async fn snipe_raydium_pool(pool_id: &str, amount: f64, jito_client: &JitoClient) -> Result<String> {
    let program_id = Pubkey::from_str("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")?;
    let tx = Transaction::new_with_payer(&[/* swap instruction */], None);
    let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
    let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
    info!("Sniped Raydium pool {}: {}", pool_id, bundle_id);
    Ok(bundle_id)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    snipe_raydium_pool("pool_id", 0.1, &jito).await?;
    Ok(())
}
