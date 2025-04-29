use anyhow::Result;
use log::info;

pub async fn analyze_sentiment(text: &str) -> Result<f64> {
    let sentiment_score = if text.to_lowercase().contains("bullish") { 0.5 } else { -0.5 };
    info!("Sentiment score for text: {}", sentiment_score);
    Ok(sentiment_score)
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    analyze_sentiment("Bullish on SOL!").await?;
    Ok(())
}
