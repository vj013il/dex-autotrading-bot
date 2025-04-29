use crate::core::jito_client::JitoClient;
use reqwest::Client;
use serde_json::json;
use anyhow::Result;
use log::{info, warn};

pub async fn simulate_bundle(jito_client: &JitoClient, transactions: Vec<Vec<u8>>) -> Result<bool> {
    let client = Client::new();
    let payload = json!({ "transactions": transactions });
    let res = client.post(format!("{}/simulateBundle", jito_client.block_engine_url))
        .json(&payload)
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    if res["status"] == "valid" {
        info!("Bundle simulation successful");
        Ok(true)
    } else {
        warn!("Bundle simulation failed: {}", res["error"]);
        Ok(false)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    simulate_bundle(&jito, vec![vec![0]]).await?;
    Ok(())
}
