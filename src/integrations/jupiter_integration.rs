use reqwest::Client;
use serde_json::Value;
use crate::core::jito_client::JitoClient;
use anyhow::Result;
use log::info;

pub async fn jupiter_swap(token_in: &str, token_out: &str, amount: f64, jito_client: &JitoClient) -> Result<String> {
    let client = Client::new();
    let quote: Value = client.get(format!("https://quote-api.jup.ag/v4/quote?inputMint={}&outputMint={}&amount={}", token_in, token_out, amount))
        .send()
        .await?
        .json()
        .await?;
    let tx = Transaction::new_with_payer(&[/* swap instruction from quote */], None);
    let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
    let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
    info!("Jupiter swap executed: {}", bundle_id);
    Ok(bundle_id)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    jupiter_swap("SOL", "USDC", 0.1, &jito).await?;
    Ok(())
}
