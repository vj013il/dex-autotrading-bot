use tokio_tungstenite::connect_async;

async fn connect_private_node(url: &str) -> Result<(), Box<dyn std::error::Error>> {
    let (ws_stream, _) = connect_async(url).await?;
    println!("Connected to private node: {}", url);
    Ok(())
}
