use ethers::providers::{Provider, Ws};
use tokio::sync::mpsc;

async fn scan_mempool(provider: Provider<Ws>, tx: mpsc::Sender<String>) {
    let mut stream = provider.subscribe_pending_txs().await.unwrap();
    while let Some(tx_hash) = stream.next().await {
        tx.send(format!("{:?}", tx_hash)).await.unwrap();
    }
}
