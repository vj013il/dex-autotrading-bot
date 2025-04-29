use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use log::info;

pub async fn verify_program(program_id: &str) -> Result<bool> {
    let client = Client::new();
    let audit: Value = client.get(format!("https://api.solana.fm/audit/{}", program_id))
        .send()
        .await?
        .json()
        .await?;
    let is_verified = audit["status"] == "verified";
    info!("Program {} audit status: {}", program_id, audit["status"]);
    Ok(is_verified)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    verify_program("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA").await?;
    Ok(())
}
