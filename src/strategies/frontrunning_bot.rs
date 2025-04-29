use crate::monitoring::mev_opportunity_monitor::MEVOpportunityMonitor;
use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use crate::core::jito_client::JitoClient;
use anyhow::Result;
use log::info;

pub async fn frontrun_trade(token_mint: &str, jito_client: &JitoClient) -> Result<String> {
    let monitor = MEVOpportunityMonitor::new();
    let large_trade = monitor.detect_large_trade(token_mint).await?;
    if large_trade.amount > 100.0 {
        let program_id = Pubkey::from_str("JUP4...")?;
        let tx = Transaction::new_with_payer(&[/* buy instruction */], None);
        let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 10000).await?;
        let bundle_id = jito_client.submit_bundle(&bundle, 10000).await?;
        info!("Frontrun trade for {}: {}", token_mint, bundle_id);
        Ok(bundle_id)
    } else {
        Ok("No frontrun".to_string())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    frontrun_trade("SOL", &jito).await?;
    Ok(())
}
