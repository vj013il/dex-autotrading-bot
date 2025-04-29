use reqwest::Client;
use serde_json::json;
use anyhow::Result;
use log::{info, error};

pub struct JitoClient {
    block_engine_url: String,
    client: Client,
}

impl JitoClient {
    pub fn new(block_engine_url: &str, _relayer_url: &str) -> Self {
        Self {
            block_engine_url: block_engine_url.to_string(),
            client: Client::new(),
        }
    }

    pub async fn submit_bundle(&self, transactions: &[Vec<u8>], tip: u64) -> Result<String> {
        let payload = json!({ "transactions": transactions, "tip": tip, "bundleOnly": true });
        let res = self.client.post(&format!("{}/submitBundle", self.block_engine_url))
            .json(&payload)
            .send()
            .await?
            .json::<serde_json::Value>()
            .await?;
        if res["status"] == "success" {
            let bundle_id = res["bundle_id"].as_str().unwrap().to_string();
            info!("Jito bundle submitted: {}", bundle_id);
            Ok(bundle_id)
        } else {
            error!("Bundle submission failed: {}", res["error"]);
            Err(anyhow::anyhow!("Bundle submission failed"))
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    jito.submit_bundle(&[vec![0]], 1000).await?;
    Ok(())
}
