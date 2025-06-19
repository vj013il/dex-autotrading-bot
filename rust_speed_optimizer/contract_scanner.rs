use ethers::providers::Provider;

async fn scan_contract(provider: Provider<Ws>, address: &str) -> bool {
    let code = provider.get_code(address, None).await.unwrap();
    !code.is_empty()
}
