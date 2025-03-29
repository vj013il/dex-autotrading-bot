// Send bundle instead of single transaction
use jito_bundle::BundleBuilder;

fn send_mev_safe_tx(orders: Vec<Order>) -> Result<()> {
    let bundle = BundleBuilder::new()
        .with_orders(orders)
        .build()?;
    
    rpc_client.send_bundle(bundle)?;
    Ok(())
}
