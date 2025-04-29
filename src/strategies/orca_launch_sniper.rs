use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use crate::core::jito_client::JitoClient;
use anyhow::Result;
use log::info;

pub async fn snipe_orca_pool(pool_address: &str, amount: f64, jito_client: &JitoClient) -> Result<String> {
    let program_id = Pubkey::from_str("9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP")?;
    let tx = Transaction::new_with_payer(&[/* swap instruction */], None);
    let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
    let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
    info!("Sniped Orca pool {}: {}", pool_address, bundle_id);
    Ok(bundle_id)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    snipe_orca_pool("pool_address", 0.1, &jito).await?;
    Ok(())
}
