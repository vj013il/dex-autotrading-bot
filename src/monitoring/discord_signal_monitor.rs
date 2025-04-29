use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use log::info;

pub async fn monitor_discord(servers: Vec<&str>) -> Result<bool> {
    let client = Client::new();
    for server in servers {
        let messages: Value = client.get(format!("https://discord.com/api/channels/{}/messages", server))
            .send()
            .await?
            .json()
            .await?;
        if messages.to_string().contains("SOL") {
            info!("Discord signal detected: {}", messages);
            return Ok(true);
        }
    }
    Ok(false)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    monitor_discord(vec!["solana_server"]).await?;
    Ok(())
}
