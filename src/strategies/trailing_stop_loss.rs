use crate::integrations::pyth_price_feed::PythPriceFeed;
use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;
use tokio::time::{sleep, Duration};

pub async fn trailing_stop_loss(token_mint: &str, trailing_percent: f64, jito_client: &JitoClient) -> Result<String> {
    let pyth = PythPriceFeed::new();
    let mut peak_price = pyth.get_price(token_mint).await?;
    loop {
        let current_price = pyth.get_price(token_mint).await?;
        if current_price > peak_price {
            peak_price = current_price;
        }
        if current_price < peak_price * (1.0 - trailing_percent) {
            let program_id = Pubkey::from_str("JUP4...")?;
            let tx = Transaction::new_with_payer(&[/* sell instruction */], None);
            let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
            let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
            info!("Trailing stop-loss triggered for {}: {}", token_mint, bundle_id);
            return Ok(bundle_id);
        }
        sleep(Duration::from_secs(60)).await;
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    trailing_stop_loss("SOL", 0.1, &jito).await?;
    Ok(())
}
