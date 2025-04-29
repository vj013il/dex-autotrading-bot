use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use crate::core::jito_client::JitoClient;
use anyhow::Result;
use log::info;

pub async fn place_serum_order(market: &str, amount: f64, jito_client: &JitoClient) -> Result<String> {
    let program_id = Pubkey::from_str("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")?;
    let tx = Transaction::new_with_payer(&[/* place order instruction */], None);
    let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
    let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
    info!("Placed Serum order on {}: {}", market, bundle_id);
    Ok(bundle_id)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    place_serum_order("SOL/USDC", 0.1, &jito).await?;
    Ok(())
}
