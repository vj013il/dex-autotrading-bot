use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn lend_solend(market_id: &str, amount: f64) -> Result<String> {
    let program_id = Pubkey::from_str("So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo")?;
    let tx = Transaction::new_with_payer(&[/* lend instruction */], None);
    let client = solana_client::rpc_client::RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let signature = client.send_and_confirm_transaction(&tx)?;
    info!("Lent {} to Solend market {}: {}", amount, market_id, signature);
    Ok(signature.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    lend_solend("market_id", 100.0).await?;
    Ok(())
}
