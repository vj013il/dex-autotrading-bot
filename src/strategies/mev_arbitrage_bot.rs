use crate::integrations::pyth_price_feed::PythPriceFeed;
use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use crate::core::jito_client::JitoClient;
use anyhow::Result;
use log::info;

pub async fn execute_arbitrage(token_mint: &str, amount: f64, jito_client: &JitoClient) -> Result<String> {
    let pyth = PythPriceFeed::new();
    let price_a = pyth.get_price(token_mint, "raydium").await?;
    let price_b = pyth.get_price(token_mint, "orca").await?;
    if price_a > price_b * 1.01 {
        let program_id = Pubkey::from_str("JUP4...")?;
        let tx_buy = Transaction::new_with_payer(&[/* buy instruction */], None);
        let tx_sell = Transaction::new_with_payer(&[/* sell instruction */], None);
        let bundle = vec![
            transaction_optimizer::optimize_transaction(tx_buy, jito_client, 10000).await?,
            transaction_optimizer::optimize_transaction(tx_sell, jito_client, 10000).await?,
        ].concat();
        let bundle_id = jito_client.submit_bundle(&bundle, 10000).await?;
        info!("Arbitrage executed for {}: {}", token_mint, bundle_id);
        Ok(bundle_id)
    } else {
        Ok("No arbitrage".to_string())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    execute_arbitrage("SOL", 0.1, &jito).await?;
    Ok(())
}
