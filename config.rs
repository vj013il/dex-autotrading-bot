use serde::Deserialize;
use std::collections::HashMap;
use std::error::Error;
use std::fs;

#[derive(Deserialize, Clone)]
pub struct Config {
    pub exchanges: Vec<String>,
    pub pairs: Vec<String>,
    pub min_spread: f64,
    pub max_order_size: f64,
    pub min_profit_usd: f64,
    pub cex_api_keys: HashMap<String, (String, String)>,
    pub dex_config: HashMap<String, String>,
    pub check_interval: f64,
    pub max_slippage: f64,
    pub solana_rpc_url: String,
}

impl Config {
    pub fn load(path: &str) -> Result<Self, Box<dyn Error>> {
        let data = fs::read_to_string(path)?;
        let config: Config = serde_json::from_str(&data)?;
        Ok(config)
    }
}
