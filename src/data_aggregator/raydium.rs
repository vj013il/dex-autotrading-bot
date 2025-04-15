use solana_client::{
    nonblocking::rpc_client::RpcClient,
    rpc_config::{RpcAccountInfoConfig, RpcProgramAccountsConfig},
    rpc_filter::{Memcmp, RpcFilterType},
};
use solana_sdk::{account::Account, pubkey::Pubkey, commitment_config::CommitmentConfig};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, sync::Arc};
use thiserror::Error;
use tokio::time::{interval, Duration};
use crate::{
    core::{CoreError, DexType, UnifiedMarketData},
    data_aggregator::{DexClient, DexConfig},
};

/// Raydium-specific AMM pool structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RaydiumPoolState {
    pub pool_id: Pubkey,
    pub base_mint: Pubkey,
    pub quote_mint: Pubkey,
    pub base_decimals: u8,
    pub quote_decimals: u8,
    pub base_reserve: u64,
    pub quote_reserve: u64,
    pub open_time: u64,
    pub market_id: Pubkey,
    pub swap_fee_numerator: u64,
    pub swap_fee_denominator: u64,
}

#[derive(Error, Debug)]
pub enum RaydiumError {
    #[error("RPC error: {0}")]
    RpcError(#[from] solana_client::client_error::ClientError),
    
    #[error("Invalid pool data: {0}")]
    InvalidPoolData(String),
    
    #[error("Numerical overflow: {0}")]
    NumericalError(String),
}

/// Raydium client implementation
pub struct RaydiumClient {
    rpc: Arc<RpcClient>,
    config: DexConfig,
    known_pools: HashMap<Pubkey, RaydiumPoolState>,
    program_id: Pubkey,
    metrics: RaydiumMetrics,
}

#[derive(Debug, Default)]
struct RaydiumMetrics {
    pools_updated: u64,
    rpc_errors: u64,
    data_errors: u64,
    last_success: Option<i64>,
}

impl RaydiumClient {
    const RAYDIUM_AMM_PROGRAM_ID: &'static str = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8";
    
    pub fn new(rpc: Arc<RpcClient>, config: DexConfig) -> Result<Self, CoreError> {
        Ok(Self {
            rpc,
            config,
            known_pools: HashMap::new(),
            program_id: Pubkey::from_str(Self::RAYDIUM_AMM_PROGRAM_ID).map_err(|e| {
                CoreError::InitializationError(format!("Invalid program ID: {}", e))
            })?,
            metrics: RaydiumMetrics::default(),
        })
    }

    /// Main data update cycle
    async fn refresh_pools(&mut self) -> Result<(), RaydiumError> {
        let filters = vec![
            RpcFilterType::Memcmp(Memcmp::new_raw_bytes(0, vec![1])), // Filter initialized pools
            RpcFilterType::DataSize(324), // Exact size of Raydium pool account
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
            match Self::parse_pool_account(&pubkey, &account) {
                Ok(pool) => {
                    new_pools.insert(pubkey, pool);
                    self.metrics.pools_updated += 1;
                }
                Err(e) => {
                    self.metrics.data_errors += 1;
                    log::warn!("Failed to parse pool {}: {}", pubkey, e);
                }
            }
        }

        self.known_pools = new_pools;
        self.metrics.last_success = Some(chrono::Utc::now().timestamp());
        Ok(())
    }

    /// Parse raw account data into pool structure
    fn parse_pool_account(pubkey: &Pubkey, account: &Account) -> Result<RaydiumPoolState, RaydiumError> {
        let data = &account.data;
        if data.len() < 324 {
            return Err(RaydiumError::InvalidPoolData("Invalid data length".into()));
        }

        let mut cursor = 8; // Skip account type and padding
        Ok(RaydiumPoolState {
            pool_id: *pubkey,
            base_mint: Pubkey::new(&data[cursor..cursor+32]),
            quote_mint: Pubkey::new(&data[cursor+32..cursor+64]),
            base_decimals: data[cursor+64],
            quote_decimals: data[cursor+65],
            base_reserve: u64::from_le_bytes(data[cursor+72..cursor+80].try_into()?),
            quote_reserve: u64::from_le_bytes(data[cursor+80..cursor+88].try_into()?),
            open_time: u64::from_le_bytes(data[cursor+88..cursor+96].try_into()?),
            market_id: Pubkey::new(&data[cursor+96..cursor+128]),
            swap_fee_numerator: u64::from_le_bytes(data[cursor+200..cursor+208].try_into()?),
            swap_fee_denominator: u64::from_le_bytes(data[cursor+208..cursor+216].try_into()?),
        })
    }

    /// Calculate price and liquidity metrics
    fn calculate_market_data(&self, pool: &RaydiumPoolState) -> Result<UnifiedMarketData, RaydiumError> {
        let base_decimals_factor = 10u64.pow(pool.base_decimals.into());
        let quote_decimals_factor = 10u64.pow(pool.quote_decimals.into());

        let base_reserve = pool.base_reserve as f64 / base_decimals_factor as f64;
        let quote_reserve = pool.quote_reserve as f64 / quote_decimals_factor as f64;

        if base_reserve <= 0.0 || quote_reserve <= 0.0 {
            return Err(RaydiumError::InvalidPoolData("Invalid reserves".into()));
        }

        let mid_price = quote_reserve / base_reserve;
        let fee_percent = (pool.swap_fee_numerator as f64 / pool.swap_fee_denominator as f64) * 100.0;

        // Calculate bid/ask with fee impact
        let price_impact = 0.01; // Temporary value, should be dynamic
        let bid_price = mid_price * (1.0 - price_impact) * (1.0 - fee_percent / 100.0);
        let ask_price = mid_price * (1.0 + price_impact) * (1.0 + fee_percent / 100.0);

        // Calculate liquidity depth
        let liquidity = (base_reserve * mid_price + quote_reserve) / 2.0;

        Ok(UnifiedMarketData {
            dex: DexType::Raydium,
            pool_address: pool.pool_id,
            base_mint: pool.base_mint,
            quote_mint: pool.quote_mint,
            bid_price,
            ask_price,
            bid_size: base_reserve * 0.01, // Temporary value
            ask_size: quote_reserve * 0.01,
            volume_24h: self.calculate_volume(pool)?,
            liquidity,
            timestamp: chrono::Utc::now().timestamp(),
        })
    }

    fn calculate_volume(&self, pool: &RaydiumPoolState) -> Result<f64, RaydiumError> {
        // TODO: Implement real volume tracking
        Ok(0.0) // Temporary implementation
    }
}

#[async_trait]
impl DexClient for RaydiumClient {
    async fn fetch_data(&self, seq_num: u64) -> Result<UnifiedMarketData, CoreError> {
        let mut interval = interval(Duration::from_millis(500));
        let mut retries = 0;

        loop {
            match self.refresh_pools().await {
                Ok(_) => break,
                Err(e) => {
                    if retries >= self.config.max_retries {
                        return Err(CoreError::AggregatorError(format!(
                            "Raydium refresh failed after {} retries: {}",
                            retries, e
                        )));
                    }
                    retries += 1;
                    interval.tick().await;
                }
            }
        }

        // Calculate weighted average prices across all pools
        let (total_bid, total_ask, total_liquidity) = self.known_pools.values()
            .filter_map(|pool| self.calculate_market_data(pool).ok())
            .fold((0.0, 0.0, 0.0), |(b, a, l), data| {
                (b + data.bid_price * data.bid_size,
                 a + data.ask_price * data.ask_size,
                 l + data.liquidity)
            });

        Ok(UnifiedMarketData {
            dex: DexType::Raydium,
            pool_address: Pubkey::default(), // Aggregated data
            base_mint: Pubkey::default(),
            quote_mint: Pubkey::default(),
            bid_price: total_bid / total_liquidity,
            ask_price: total_ask / total_liquidity,
            bid_size: total_liquidity,
            ask_size: total_liquidity,
            volume_24h: 0.0, // TODO: Implement
            liquidity: total_liquidity,
            timestamp: chrono::Utc::now().timestamp(),
        })
    }
}

// Implementation details for error conversions
impl From<RaydiumError> for CoreError {
    fn from(e: RaydiumError) -> Self {
        CoreError::AggregatorError(format!("Raydium error: {}", e))
    }
}

// Unit tests with mock data
#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::account::Account;

    fn mock_pool_account() -> Account {
        let mut data = vec![0u8; 324];
        // Populate with test data
        data[8..40].copy_from_slice(&[1u8; 32]); // base_mint
        data[40..72].copy_from_slice(&[2u8; 32]); // quote_mint
        data[72] = 6; // base_decimals
        data[73] = 6; // quote_decimals
        data[80..88].copy_from_slice(&1000u64.to_le_bytes()); // base_reserve
        data[88..96].copy_from_slice(&2000u64.to_le_bytes()); // quote_reserve
        data[200..208].copy_from_slice(&25u64.to_le_bytes()); // fee numerator
        data[208..216].copy_from_slice(&10000u64.to_le_bytes()); // fee denominator
        Account {
            data,
            ..Account::default()
        }
    }

    #[tokio::test]
    async fn test_pool_parsing() {
        let pubkey = Pubkey::new_unique();
        let account = mock_pool_account();
        let pool = RaydiumClient::parse_pool_account(&pubkey, &account).unwrap();
        
        assert_eq!(pool.base_reserve, 1000);
        assert_eq!(pool.quote_reserve, 2000);
        assert_eq!(pool.swap_fee_numerator, 25);
        assert_eq!(pool.swap_fee_denominator, 10000);
    }
}
