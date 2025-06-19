use ethers::signers::{LocalWallet, Signer};
use ethers::types::{TransactionRequest, H256};
use tokio::time::Instant;

async fn process_transaction(wallet: &LocalWallet, tx: TransactionRequest) -> Result<H256, Box<dyn std::error::Error>> {
    let start = Instant::now();
    let signed_tx = wallet.sign_transaction(&tx).await?;
    let tx_hash = signed_tx.hash();
    println!("Transaction signed in {} micros", start.elapsed().as_micros());
    Ok(tx_hash)
}
