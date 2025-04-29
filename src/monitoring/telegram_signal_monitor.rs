use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use log::info;

pub async fn monitor_telegram(channels: Vec<&str>) -> Result<bool> {
    let client = Client::new();
    for channel in channels {
        let messages: Value = client.get(format!("https://api.telegram.org/bot.../getMessages?chat_id={}", channel))
            .send()
            .await?
            .json()
            .await?;
        if messages.to_string().contains("SOL") {
            info!("Telegram signal detected: {}", messages);
            return Ok(true);
        }
    }
    Ok(false)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    monitor_telegram(vec!["solana_channel"]).await?;
    Ok(())
}
