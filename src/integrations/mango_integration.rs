use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn stake_marinade(amount: f64) -> Result<String> {
    let program_id = Pubkey::from_str("MarBmsSgKXdrN1egZf5sqe1TMThrzekxdqA1jFzSy")?;
    let tx = Transaction::new_with_payer(&[/* stake instruction */], None);
    let client = solana_client::rpc_client::RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    let signature = client.send_and_confirm_transaction(&tx)?;
    info!("Staked {} SOL in Marinade: {}", amount, signature);
    Ok(signature.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    stake_marinade(1.0).await?;
    Ok(())
}
