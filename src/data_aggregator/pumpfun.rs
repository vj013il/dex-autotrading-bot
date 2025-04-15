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

/// Pump.fun bonding curve parameters
const PUMPFUN_PROGRAM_ID: &str = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P";
const BASE_FEE_BPS: u64 = 200; // 2% fee
const CURVE_FACTOR: f64 = 0.0001;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PumpFunPoolState {
    pub pool_address: Pubkey,
    pub base_mint: Pubkey,
    pub quote_mint: Pubkey,
    pub total_supply: u64,
    pub base_decimals: u8,
    pub quote_decimals: u8,
    pub curve_parameter: f64,
    pub creator_fee_bps: u16,
    pub accumulated_fees: u64,
    pub last_trade_timestamp: i64,
}

#[derive(Error, Debug)]
pub enum PumpFunError {
    #[error("RPC error: {0}")]
    RpcError(#[from] solana_client::client_error::ClientError),
    
    #[error("Invalid pool data: {0}")]
    InvalidPoolData(String),
    
    #[error("Numerical error: {0}")]
    NumericalError(String),
}

pub struct PumpFunClient {
    rpc: Arc<RpcClient>,
    config: DexConfig,
    known_pools: HashMap<Pubkey, PumpFunPoolState>,
    program_id: Pubkey,
    metrics: PumpFunMetrics,
}

#[derive(Debug, Default)]
struct PumpFunMetrics {
    pools_updated: u64,
    rpc_errors: u64,
    data_errors: u64,
    last_success: Option<i64>,
}

impl PumpFunClient {
    pub fn new(rpc: Arc<RpcClient>, config: DexConfig) -> Result<Self, CoreError> {
        Ok(Self {
            rpc,
            config,
            known_pools: HashMap::new(),
            program_id: Pubkey::from_str(PUMPFUN_PROGRAM_ID).map_err(|e| {
                CoreError::InitializationError(format!("Invalid Pump.fun program ID: {}", e))
            })?,
            metrics: PumpFunMetrics::default(),
        })
    }

    async fn refresh_pools(&mut self) -> Result<(), PumpFunError> {
        let filters = vec![
            RpcFilterType::Memcmp(Memcmp::new_raw_bytes(0, vec![1])),
            RpcFilterType::DataSize(128), // Actual size may vary
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
                    log::warn!("Failed to parse Pump.fun pool {}: {}", pubkey, e);
                }
            }
        }

        self.known_pools = new_pools;
        self.metrics.last_success = Some(chrono::Utc::now().timestamp());
        Ok(())
    }

    fn parse_pool_account(pubkey: &Pubkey, account: &Account) -> Result<PumpFunPoolState, PumpFunError> {
        let data = &account.data;
        if data.len() < 128 {
            return Err(PumpFunError::InvalidPoolData("Invalid data length".into()));
        }

        let mut cursor = 8; // Skip account type and version
        Ok(PumpFunPoolState {
            pool_address: *pubkey,
            base_mint: Pubkey::new(&data[cursor..cursor+32]),
            quote_mint: Pubkey::new(&data[cursor+32..cursor+64]),
            total_supply: u64::from_le_bytes(data[cursor+64..cursor+72].try_into()?),
            base_decimals: data[cursor+72],
            quote_decimals: data[cursor+73],
            curve_parameter: f64::from_le_bytes(data[cursor+74..cursor+82].try_into()?),
            creator_fee_bps: u16::from_le_bytes(data[cursor+82..cursor+84].try_into()?),
            accumulated_fees: u64::from_le_bytes(data[cursor+84..cursor+92].try_into()?),
            last_trade_timestamp: i64::from_le_bytes(data[cursor+92..cursor+100].try_into()?),
        })
    }

    fn calculate_price(&self, pool: &PumpFunPoolState) -> Result<f64, PumpFunError> {
        // Bonding curve formula: price = (total_supply * curve_parameter) + CURVE_FACTOR
        let base = pool.total_supply as f64 * pool.curve_parameter;
        let price = base + CURVE_FACTOR;
        
        if price <= 0.0 {
            return Err(PumpFunError::NumericalError("Invalid price calculation".into()));
        }

        Ok(price)
    }

    fn calculate_volume(&self, pool: &PumpFunPoolState) -> f64 {
        // Estimated volume based on accumulated fees
        let fee_percent = (BASE_FEE_BPS + pool.creator_fee_bps as u64) as f64 / 10000.0;
        pool.accumulated_fees as f64 / fee_percent
    }

    fn convert_decimals(&self, amount: f64, decimals: u8) -> f64 {
        amount / 10f64.powi(decimals as i32)
    }
}

#[async_trait]
impl DexClient for PumpFunClient {
    async fn fetch_data(&self, seq_num: u64) -> Result<UnifiedMarketData, CoreError> {
        let mut retries = 0;
        let mut interval = tokio::time::interval(Duration::from_millis(500));
        
        loop {
            match self.refresh_pools().await {
                Ok(_) => break,
                Err(e) => {
                    if retries >= self.config.max_retries {
                        return Err(CoreError::AggregatorError(format!(
                            "Pump.fun refresh failed after {} retries: {}",
                            retries, e
                        )));
                    }
                    retries += 1;
                    interval.tick().await;
                }
            }
        }

        let (total_bid, total_ask, total_liquidity) = self.known_pools.values()
            .filter_map(|pool| {
                let price = self.calculate_price(pool).ok()?;
                let volume = self.calculate_volume(pool);
                
                Some(UnifiedMarketData {
                    dex: DexType::PumpFun,
                    pool_address: pool.pool_address,
                    base_mint: pool.base_mint,
                    quote_mint: pool.quote_mint,
                    bid_price: price * 0.98, // Account for fees
                    ask_price: price * 1.02,
                    bid_size: self.convert_decimals(pool.total_supply as f64, pool.base_decimals),
                    ask_size: volume,
                    volume_24h: volume,
                    liquidity: price * self.convert_decimals(pool.total_supply as f64, pool.base_decimals),
                    timestamp: pool.last_trade_timestamp,
                })
            })
            .fold((0.0, 0.0, 0.0), |(b, a, l), data| {
                (b + data.bid_price, a + data.ask_price, l + data.liquidity)
            });

        Ok(UnifiedMarketData {
            dex: DexType::PumpFun,
            pool_address: Pubkey::default(),
            base_mint: Pubkey::default(),
            quote_mint: Pubkey::default(),
            bid_price: total_bid / total_liquidity,
            ask_price: total_ask / total_liquidity,
            bid_size: total_liquidity,
            ask_size: total_liquidity,
            volume_24h: self.known_pools.values()
                .map(|p| self.calculate_volume(p))
                .sum(),
            liquidity: total_liquidity,
            timestamp: chrono::Utc::now().timestamp(),
        })
    }
}

impl From<PumpFunError> for CoreError {
    fn from(e: PumpFunError) -> Self {
        CoreError::AggregatorError(format!("Pump.fun error: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::account::Account;

    fn mock_pumpfun_account() -> Account {
        let mut data = vec![0u8; 128];
        // Populate test data
        data[8..40].copy_from_slice(&[1u8; 32]);  // base_mint
        data[40..72].copy_from_slice(&[2u8; 32]); // quote_mint
        data[64..72].copy_from_slice(&1000u64.to_le_bytes()); // total_supply
        data[72] = 6; // base_decimals
        data[73] = 6; // quote_decimals
        data[74..82].copy_from_slice(&0.0001f64.to_le_bytes()); // curve_parameter
        data[82..84].copy_from_slice(&500u16.to_le_bytes()); // creator_fee_bps
        data[84..92].copy_from_slice(&1000000u64.to_le_bytes()); // accumulated_fees
        Account { data, ..Account::default() }
    }

    #[tokio::test]
    async fn test_pumpfun_parsing() {
        let pubkey = Pubkey::new_unique();
        let account = mock_pumpfun_account();
        let pool = PumpFunClient::parse_pool_account(&pubkey, &account).unwrap();
        
        assert_eq!(pool.total_supply, 1000);
        assert_eq!(pool.curve_parameter, 0.0001);
        assert_eq!(pool.creator_fee_bps, 500);
    }

    #[tokio::test]
    async fn test_price_calculation() {
        let client = PumpFunClient::new(Arc::new(RpcClient::new("test")), DexConfig::default()).unwrap();
        let pool = PumpFunPoolState {
            total_supply: 1000,
            curve_parameter: 0.0001,
            ..Default::default()
        };
        
        let price = client.calculate_price(&pool).unwrap();
        assert!((price - (1000.0 * 0.0001 + 0.0001)).abs() < f64::EPSILON);
    }
}
