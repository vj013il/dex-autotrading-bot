use solana_sdk::transaction::Transaction;
use jito_rust_sdk::JitoClient;
use anyhow::Result;
use log::{info, error};

pub async fn optimize_transaction(tx: Transaction, jito_client: &JitoClient, tip: u64) -> Result<Vec<Vec<u8>>> {
    let bundle = vec![tx.serialize()];
    match jito_client.submit_bundle(&bundle, tip).await {
        Ok(bundle_id) => {
            info!("Optimized transaction with Jito bundle: {}", bundle_id);
            Ok(bundle)
        }
        Err(e) => {
            error!("Error optimizing transaction: {}", e);
            Err(e.into())
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    optimize_transaction(Transaction::new_unsigned(), &jito, 1000).await?;
    Ok(())
}
