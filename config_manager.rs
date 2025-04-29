use serde::{Deserialize, Serialize};
use anyhow::Result;
use log::info;

#[derive(Serialize, Deserialize)]
pub struct Config {
    solana_rpc: String,
    jito_block_engine: String,
    jito_relayer: String,
    api_keys: std::collections::HashMap<String, String>,
}

pub struct ConfigManager {
    config: Config,
}

impl ConfigManager {
    pub fn new() -> Self {
        Self {
            config: Config {
                solana_rpc: "https://api.mainnet-beta.solana.com".to_string(),
                jito_block_engine: "https://block-engine.jito.wtf".to_string(),
                jito_relayer: "https://relayer.jito.wtf".to_string(),
                api_keys: std::collections::HashMap::from([("jito".to_string(), "your_jito_api_key".to_string())]),
            },
        }
    }

    pub fn get_config(&self, key: &str) -> Result<String> {
        let value = self.config.api_keys.get(key).cloned()
            .or_else(|| match key {
                "solana_rpc" => Some(self.config.solana_rpc.clone()),
                "jito_block_engine" => Some(self.config.jito_block_engine.clone()),
                "jito_relayer" => Some(self.config.jito_relayer.clone()),
                _ => None,
            })
            .ok_or_else(|| anyhow::anyhow!("Key not found"))?;
        info!("Retrieved config for {}", key);
        Ok(value)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let config = ConfigManager::new();
    config.get_config("jito_block_engine")?;
    Ok(())
}
