use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use log::info;

pub async fn monitor_x_signals(token_symbol: &str, reputation_threshold: f64) -> Result<bool> {
    let client = Client::new();
    let posts: Value = client.get("https://api.x.com/posts")
        .query(&[("query", token_symbol)])
        .send()
        .await?
        .json()
        .await?;
    if let Some(post_array) = posts.as_array() {
        for post in post_array {
            if post["author_reputation"].as_f64().unwrap_or(0.0) > reputation_threshold {
                info!("X signal detected for {}: {}", token_symbol, post["content"]);
                return Ok(true);
            }
        }
    }
    Ok(false)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    monitor_x_signals("SOL", 0.8).await?;
    Ok(())
}
