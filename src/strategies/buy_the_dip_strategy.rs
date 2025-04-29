use crate::integrations::pyth_price_feed::PythPriceFeed;
use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn buy_the_dip(token_mint: &str, dip_threshold: f64, jito_client: &JitoClient) -> Result<String> {
    let pyth = PythPriceFeed::new();
    let historical_price = pyth.get_historical_price(token_mint, 3600).await?;
    let current_price = pyth.get_price(token_mint).await?;
    if (historical_price - current_price) / historical_price > dip_threshold {
        let program_id = Pubkey::from_str("JUP4...")?;
        let tx = Transaction::new_with_payer(&[/* buy instruction */], None);
        let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
        let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
        info!("Bought dip for {}: {}", token_mint, bundle_id);
        Ok(bundle_id)
    } else {
        Ok("No dip".to_string())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    buy_the_dip("SOL", 0.1, &jito).await?;
    Ok(())
}
