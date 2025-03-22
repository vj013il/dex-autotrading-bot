fn cross_chain_arbitrage(
    src_chain: Chain,
    dest_chain: Chain,
    asset: &str,
    amount: f64
) -> Result<f64, Error> {
    let price_src = src_chain.get_price(asset);
    let price_dest = dest_chain.get_price(asset);
    if price_dest > price_src * 1.01 {
        let tx_hash = bridge_asset(src_chain, dest_chain, asset, amount);
        dest_chain.sell(asset, amount);
        Ok(profit)
    } else {
        Err(Error::NoArbOpportunity)
    }
}
