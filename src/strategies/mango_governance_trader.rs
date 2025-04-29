use reqwest::Client;
use serde_json::Value;
use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn trade_on_mango_governance(proposal_id: u64, amount: f64) -> Result<String> {
    let client = Client::new();
    let proposal: Value = client.get(format!("https://api.mango.markets/governance/{}", proposal_id))
        .send()
        .await?
        .json()
        .await?;
    if proposal["status"] == "passed" && proposal["description"].to_string().contains("favorable") {
        let program_id = Pubkey::from_str("MangoDAoqz2gAc86yL8NsoEXnA3r7i7NqM6m97pV8AMU")?;
        let tx = Transaction::new_with_payer(&[/* buy instruction */], None);
        let client = solana_client::rpc_client::RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
        let signature = client.send_and_confirm_transaction(&tx)?;
        info!("Traded MNGO on governance outcome: {}", signature);
        Ok(signature.to_string())
    } else {
        Ok("No trade".to_string())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    trade_on_mango_governance(123, 0.1).await?;
    Ok(())
}
