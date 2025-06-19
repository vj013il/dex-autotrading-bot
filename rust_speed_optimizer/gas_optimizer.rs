use ethers::providers::Provider;
use ethers::types::U256;

async fn optimize_gas(provider: Provider<Ws>) -> U256 {
    let gas_price = provider.get_gas_price().await.unwrap();
    gas_price + (gas_price / U256::from(10)) // Add 10% premium
}
