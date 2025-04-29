use solana_sdk::{transaction::Transaction, pubkey::Pubkey};
use anyhow::Result;
use log::info;

pub async fn rebalance_portfolio(tokens: Vec<&str>, target_weights: Vec<f64>, jito_client: &JitoClient) -> Result<String> {
    let client = solana_client::rpc_client::RpcClient::new("https://api.mainnet-beta.solana.com".to_string());
    for (token, weight) in tokens.iter().zip(target_weights.iter()) {
        let balance = client.get_token_account_balance(&token.parse()?)?;
        let target_balance = balance.ui_amount.unwrap() * weight;
        let program_id = Pubkey::from_str("JUP4...")?;
        let tx = Transaction::new_with_payer(
            &[/* buy/sell instruction based on balance vs target */],
            None,
        );
        let bundle = transaction_optimizer::optimize_transaction(tx, jito_client, 5000).await?;
        let bundle_id = jito_client.submit_bundle(&bundle, 5000).await?;
        info!("Rebalanced {}: {}", token, bundle_id);
        return Ok(bundle_id);
    }
    Ok("No rebalance".to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let jito = JitoClient::new("https://block-engine.jito.wtf", "https://relayer.jito.wtf");
    rebalance_portfolio(vec!["SOL", "USDC"], vec![0.6, 0.4], &jito).await?;
    Ok(())
}
