use tokio_tungstenite::tungstenite::Message;

async fn handle_ws_message(msg: Message) {
    if let Message::Text(text) = msg {
        println!("Received: {}", text);
    }
}
