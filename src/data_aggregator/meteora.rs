use solana_client::{
    nonblocking::rpc_client::RpcClient,
    rpc_config::{RpcAccountInfoConfig, RpcProgramAccountsConfig},
    rpc_filter::{Memcmp, RpcFilterType},
};
use solana_sdk::{account::Account, pubkey::Pubkey, commitment_config::CommitmentConfig};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, sync::Arc, str::FromStr};
use thiserror::Error;
use crate::{
    core::{CoreError, DexType, UnifiedMarketData},
    data_aggregator::{DexClient, DexConfig},
};

/// Meteora DLMM constants
const DLMM_PROGRAM_ID: &str = "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi";
const BIN_STEP_SCALE: u16 = 100;
const PROTOCOL_FEE_SCALE: u16 = 10_000;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DlmmPoolState {
    pub address: Pubkey,
    pub base_mint: Pubkey,
    pub quote_mint: Pubkey,
    pub bin_step: u16,
    pub active_bins: Vec<BinState>,
    pub fee_rate: u16,
    pub protocol_fee: u64,
    pub base_decimals: u8,
    pub quote_decimals: u8,
    pub last_updated_slot: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinState {
    pub id: i32,
    pub price: f64,
    pub base_liquidity: u64,
    pub quote_liquidity: u64,
}

#[derive(Error, Debug)]
pub enum MeteoraError {
    #[error("RPC error: {0}")]
    RpcError(#[from] solana_client::client_error::ClientError),
    
    #[error("Invalid pool data: {0}")]
    InvalidPoolData(String),
    
    #[error("Bin calculation error: {0}")]
    BinError(String),
}

pub struct MeteoraClient {
    rpc: Arc<RpcClient>,
    config: DexConfig,
    known_pools: HashMap<Pubkey, DlmmPoolState>,
    program_id: Pubkey,
    metrics: MeteoraMetrics,
}

#[derive(Debug, Default)]
struct MeteoraMetrics {
    pools_updated: u64,
    bins_processed: u64,
    rpc_errors: u64,
    last_success: Option<i64>,
}

impl MeteoraClient {
    pub fn new(rpc: Arc<RpcClient>, config: DexConfig) -> Result<Self, CoreError> {
        Ok(Self {
            rpc,
            config,
            known_pools: HashMap::new(),
            program_id: Pubkey::from_str(DLMM_PROGRAM_ID).map_err(|e| {
                CoreError::InitializationError(format!("Invalid Meteora program ID: {}", e))
            })?,
            metrics: MeteoraMetrics::default(),
        })
    }

    async fn refresh_pools(&mut self) -> Result<(), MeteoraError> {
        let filters = vec![
            RpcFilterType::Memcmp(Memcmp::new_raw_bytes(0, vec![1]) // Initialized pools
        ];

        let config = RpcProgramAccountsConfig {
            filters: Some(filters),
            account_config: RpcAccountInfoConfig {
                commitment: Some(CommitmentConfig::confirmed()),
                encoding: Some(solana_account_decoder::UiAccountEncoding::Base64),
                ..Default::default()
            },
            ..Default::default()
        };

        let accounts = self.rpc
            .get_program_accounts_with_config(&self.program_id, config)
            .await?;

        let mut new_pools = HashMap::new();
        for (pubkey, account) in accounts {
            match Self::parse_dlmm_account(&pubkey, &account) {
                Ok(pool) => {
                    self.metrics.bins_processed += pool.active_bins.len() as u64;
                    new_pools.insert(pubkey, pool);
                    self.metrics.pools_updated += 1;
                }
                Err(e) => {
                    self.metrics.rpc_errors += 1;
                    log::warn!("Failed to parse Meteora pool {}: {}", pubkey, e);
                }
            }
        }

        self.known_pools = new_pools;
        self.metrics.last_success = Some(chrono::Utc::now().timestamp());
        Ok(())
    }

    fn parse_dlmm_account(pubkey: &Pubkey, account: &Account) -> Result<DlmmPoolState, MeteoraError> {
        let data = &account.data;
        if data.len() < 256 {
            return Err(MeteoraError::InvalidPoolData("Invalid data length".into()));
        }

        let mut cursor = 8; // Skip header
        let bin_step = u16::from_le_bytes(data[cursor..cursor+2].try_into()?);
        cursor += 2;
        
        let base_mint = Pubkey::new(&data[cursor..cursor+32]);
        cursor += 32;
        
        let quote_mint = Pubkey::new(&data[cursor..cursor+32]);
        cursor += 32;
        
        let fee_rate = u16::from_le_bytes(data[cursor..cursor+2].try_into()?);
        cursor += 2;
        
        let protocol_fee = u64::from_le_bytes(data[cursor..cursor+8].try_into()?);
        cursor += 8;
        
        let base_decimals = data[cursor];
        cursor += 1;
        
        let quote_decimals = data[cursor];
        cursor += 1;
        
        // Parse active bins (simplified)
        let bin_count = u16::from_le_bytes(data[cursor..cursor+2].try_into()?) as usize;
        cursor += 2;
        
        let mut active_bins = Vec::with_capacity(bin_count);
        for _ in 0..bin_count {
            let id = i32::from_le_bytes(data[cursor..cursor+4].try_into()?);
            cursor += 4;
            
            let price = f64::from_le_bytes(data[cursor..cursor+8].try_into()?);
            cursor += 8;
            
            let base_liquidity = u64::from_le_bytes(data[cursor..cursor+8].try_into()?);
            cursor += 8;
            
            let quote_liquidity = u64::from_le_bytes(data[cursor..cursor+8].try_into()?);
            cursor += 8;
            
            active_bins.push(BinState {
                id,
                price,
                base_liquidity,
                quote_liquidity,
            });
        }

        Ok(DlmmPoolState {
            address: *pubkey,
            base_mint,
            quote_mint,
            bin_step,
            active_bins,
            fee_rate,
            protocol_fee,
            base_decimals,
            quote_decimals,
            last_updated_slot: u64::from_le_bytes(data[cursor..cursor+8].try_into()?),
        })
    }

    fn calculate_market_data(&self, pool: &DlmmPoolState) -> Result<UnifiedMarketData, MeteoraError> {
        let (best_bid, best_ask) = self.find_best_prices(pool)?;
        let (total_bid, total_ask, total_liquidity) = self.aggregate_liquidity(pool);

        Ok(UnifiedMarketData {
            dex: DexType::Meteora,
            pool_address: pool.address,
            base_mint: pool.base_mint,
            quote_mint: pool.quote_mint,
            bid_price: best_bid,
            ask_price: best_ask,
            bid_size: total_bid,
            ask_size: total_ask,
            volume_24h: self.estimate_volume(pool),
            liquidity: total_liquidity,
            timestamp: chrono::Utc::now().timestamp(),
        })
    }

    fn find_best_prices(&self, pool: &DlmmPoolState) -> Result<(f64, f64), MeteoraError> {
        let mut best_bid = 0.0;
        let mut best_ask = f64::MAX;
        
        for bin in &pool.active_bins {
            if bin.quote_liquidity > 0 {
                best_bid = best_bid.max(bin.price);
            }
            if bin.base_liquidity > 0 {
                best_ask = best_ask.min(bin.price);
            }
        }
        
        if best_ask == f64::MAX || best_bid == 0.0 {
            return Err(MeteoraError::BinError("No valid bins found".into()));
        }
        
        Ok((best_bid, best_ask))
    }

    fn aggregate_liquidity(&self, pool: &DlmmPoolState) -> (f64, f64, f64) {
        let (total_bid, total_ask, total_liquidity) = pool.active_bins.iter().fold(
            (0.0, 0.0, 0.0),
            |(bid, ask, liq), bin| {
                let base = self.convert_amount(bin.base_liquidity as f64, pool.base_decimals);
                let quote = self.convert_amount(bin.quote_liquidity as f64, pool.quote_decimals);
                
                (
                    bid + quote,
                    ask + base,
                    liq + (base * bin.price + quote),
                )
            },
        );
        
        (total_bid, total_ask, total_liquidity)
    }

    fn convert_amount(&self, amount: f64, decimals: u8) -> f64 {
        amount / 10f64.powi(decimals as i32)
    }

    fn estimate_volume(&self, pool: &DlmmPoolState) -> f64 {
        let fee_value = self.convert_amount(pool.protocol_fee as f64, pool.quote_decimals);
        fee_value / (pool.fee_rate as f64 / PROTOCOL_FEE_SCALE as f64)
    }
}

#[async_trait]
impl DexClient for MeteoraClient {
    async fn fetch_data(&self, seq_num: u64) -> Result<UnifiedMarketData, CoreError> {
        let mut retries = 0;
        let mut interval = tokio::time::interval(Duration::from_millis(500));
        
        loop {
            match self.refresh_pools().await {
                Ok(_) => break,
                Err(e) => {
                    if retries >= self.config.max_retries {
                        return Err(CoreError::AggregatorError(format!(
                            "Meteora refresh failed after {} retries: {}",
                            retries, e
                        )));
                    }
                    retries += 1;
                    interval.tick().await;
                }
            }
        }

        let (total_bid, total_ask, total_liquidity) = self.known_pools.values()
            .filter_map(|pool| self.calculate_market_data(pool).ok())
            .fold((0.0, 0.0, 0.0), |(b, a, l), data| {
                (b + data.bid_price, a + data.ask_price, l + data.liquidity)
            });

        Ok(UnifiedMarketData {
            dex: DexType::Meteora,
            pool_address: Pubkey::default(),
            base_mint: Pubkey::default(),
            quote_mint: Pubkey::default(),
            bid_price: total_bid / total_liquidity,
            ask_price: total_ask / total_liquidity,
            bid_size: total_liquidity,
            ask_size: total_liquidity,
            volume_24h: self.known_pools.values()
                .map(|p| self.estimate_volume(p))
                .sum(),
            liquidity: total_liquidity,
            timestamp: chrono::Utc::now().timestamp(),
        })
    }
}

impl From<MeteoraError> for CoreError {
    fn from(e: MeteoraError) -> Self {
        CoreError::AggregatorError(format!("Meteora error: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::account::Account;

    fn mock_dlmm_account() -> Account {
        let mut data = vec![0u8; 256];
        // Populate test data
        data[8..10].copy_from_slice(&100u16.to_le_bytes()); // bin_step
        data[10..42].copy_from_slice(&[1u8; 32]); // base_mint
        data[42..74].copy_from_slice(&[2u8; 32]); // quote_mint
        data[74..76].copy_from_slice(&300u16.to_le_bytes()); // fee_rate (3%)
        data[76..84].copy_from_slice(&100_000u64.to_le_bytes()); // protocol_fee
        data[84] = 6; // base_decimals
        data[85] = 6; // quote_decimals
        data[86..88].copy_from_slice(&1u16.to_le_bytes()); // bin_count
        
        // Add single bin
        data[88..92].copy_from_slice(&0i32.to_le_bytes()); // bin ID
        data[92..100].copy_from_slice(&100.0f64.to_le_bytes()); // price
        data[100..108].copy_from_slice(&1_000_000u64.to_le_bytes()); // base_liquidity
        data[108..116].copy_from_slice(&100_000_000u64.to_le_bytes()); // quote_liquidity
        
        Account { data, ..Account::default() }
    }

    #[tokio::test]
    async fn test_dlmm_parsing() {
        let pubkey = Pubkey::new_unique();
        let account = mock_dlmm_account();
        let pool = MeteoraClient::parse_dlmm_account(&pubkey, &account).unwrap();
        
        assert_eq!(pool.bin_step, 100);
        assert_eq!(pool.fee_rate, 300);
        assert_eq!(pool.active_bins.len(), 1);
    }

    #[tokio::test]
    async fn test_price_calculation() {
        let client = MeteoraClient::new(Arc::new(RpcClient::new("test")), DexConfig::default()).unwrap();
        let pool = DlmmPoolState {
            active_bins: vec![
                BinState {
                    id: 0,
                    price: 100.0,
                    base_liquidity: 1_000_000,
                    quote_liquidity: 100_000_000,
                }
            ],
            base_decimals: 6,
            quote_decimals: 6,
            ..Default::default()
        };
        
        let data = client.calculate_market_data(&pool).unwrap();
        assert!((data.bid_price - 100.0).abs() < f64::EPSILON);
    }
}
