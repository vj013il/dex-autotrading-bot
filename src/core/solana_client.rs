use solana_client::rpc_client::RpcClient;
use solana_sdk::commitment_config::CommitmentConfig;
use anyhow::Result;
use log::info;

pub struct SolanaClient {
    client: RpcClient,
}

impl SolanaClient {
    pub fn new(rpc_url: &str) -> Result<Self> {
        let client = RpcClient::new_with_commitment(rpc_url.to_string(), CommitmentConfig::confirmed());
        info!("Solana client initialized");
        Ok(Self { client })
    }

    pub async fn get_balance(&self, pubkey: &str) -> Result<u64> {
        let pubkey = pubkey.parse()?;
        let balance = self.client.get_balance(&pubkey)?;
        info!("Balance for {}: {} lamports", pubkey, balance);
        Ok(balance)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let client = SolanaClient::new("https://api.mainnet-beta.solana.com")?;
    client.get_balance("pubkey").await?;
    Ok(())
}
