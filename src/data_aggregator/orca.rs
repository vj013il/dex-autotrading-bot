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

/// Orca Whirlpool constants
const WHIRLPOOL_PROGRAM_ID: &str = "whirLbMiicVdio2qvUfQQ5KJ3LxVDgnjX6QZH5TzTR";
const FEE_SCALE: u128 = 1_000_000;
const TICK_SCALE: i32 = 100;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhirlpoolState {
    pub address: Pubkey,
    pub token_mint_a: Pubkey,
    pub token_mint_b: Pubkey,
    pub tick_spacing: u16,
    pub liquidity: u128,
    pub sqrt_price: u128,
    pub fee_rate: u16,
    pub protocol_fee: u64,
    pub decimals_a: u8,
    pub decimals_b: u8,
    pub last_updated_slot: u64,
}

#[derive(Error, Debug)]
pub enum OrcaError {
    #[error("RPC error: {0}")]
    RpcError(#[from] solana_client::client_error::ClientError),
    
    #[error("Invalid pool data: {0}")]
    InvalidPoolData(String),
    
    #[error("Tick math error: {0}")]
    TickError(String),
}

pub struct OrcaClient {
    rpc: Arc<RpcClient>,
    config: DexConfig,
    known_pools: HashMap<Pubkey, WhirlpoolState>,
    program_id: Pubkey,
    metrics: OrcaMetrics,
}

#[derive(Debug, Default)]
struct OrcaMetrics {
    pools_updated: u64,
    rpc_errors: u64,
    data_errors: u64,
    last_success: Option<i64>,
}

impl OrcaClient {
    pub fn new(rpc: Arc<RpcClient>, config: DexConfig) -> Result<Self, CoreError> {
        Ok(Self {
            rpc,
            config,
            known_pools: HashMap::new(),
            program_id: Pubkey::from_str(WHIRLPOOL_PROGRAM_ID).map_err(|e| {
                CoreError::InitializationError(format!("Invalid Orca program ID: {}", e))
            })?,
            metrics: OrcaMetrics::default(),
        })
    }

    async fn refresh_pools(&mut self) -> Result<(), OrcaError> {
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
            match Self::parse_whirlpool_account(&pubkey, &account) {
                Ok(pool) => {
                    new_pools.insert(pubkey, pool);
                    self.metrics.pools_updated += 1;
                }
                Err(e) => {
                    self.metrics.data_errors += 1;
                    log::warn!("Failed to parse Orca pool {}: {}", pubkey, e);
                }
            }
        }

        self.known_pools = new_pools;
        self.metrics.last_success = Some(chrono::Utc::now().timestamp());
        Ok(())
    }

    fn parse_whirlpool_account(pubkey: &Pubkey, account: &Account) -> Result<WhirlpoolState, OrcaError> {
        let data = &account.data;
        if data.len() < 344 {
            return Err(OrcaError::InvalidPoolData("Invalid data length".into()));
        }

        Ok(WhirlpoolState {
            address: *pubkey,
            token_mint_a: Pubkey::new(&data[8..40]),
            token_mint_b: Pubkey::new(&data[40..72]),
            tick_spacing: u16::from_le_bytes(data[72..74].try_into()?),
            liquidity: u128::from_le_bytes(data[104..120].try_into()?),
            sqrt_price: u128::from_le_bytes(data[120..136].try_into()?),
            fee_rate: u16::from_le_bytes(data[144..146].try_into()?),
            protocol_fee: u64::from_le_bytes(data[152..160].try_into()?),
            decimals_a: data[168],
            decimals_b: data[169],
            last_updated_slot: u64::from_le_bytes(data[176..184].try_into()?),
        })
    }

    fn calculate_price(&self, pool: &WhirlpoolState) -> Result<f64, OrcaError> {
        // Convert sqrtPrice to actual price
        let sqrt_price = pool.sqrt_price as f64 / 2f64.powi(64);
        let price = sqrt_price.powi(2);
        
        // Adjust for token decimals
        let decimals_diff = i32::from(pool.decimals_a) - i32::from(pool.decimals_b);
        let scaled_price = price * 10f64.powi(decimals_diff);
        
        Ok(scaled_price)
    }

    fn calculate_depth(&self, pool: &WhirlpoolState) -> (f64, f64) {
        // Calculate liquidity depth based on tick spacing
        let base_liquidity = self.convert_amount(pool.liquidity as f64, pool.decimals_a);
        let quote_liquidity = self.convert_amount(
            pool.liquidity as f64 * self.sqrt_price_to_tick(pool.sqrt_price),
            pool.decimals_b
        );
        
        (base_liquidity, quote_liquidity)
    }

    fn sqrt_price_to_tick(&self, sqrt_price: u128) -> f64 {
        let tick = (sqrt_price as f64).log2() / (1.0001f64.ln()).sqrt();
        tick * TICK_SCALE as f64
    }

    fn convert_amount(&self, amount: f64, decimals: u8) -> f64 {
        amount / 10f64.powi(decimals as i32)
    }
}

#[async_trait]
impl DexClient for OrcaClient {
    async fn fetch_data(&self, seq_num: u64) -> Result<UnifiedMarketData, CoreError> {
        let mut retries = 0;
        let mut interval = tokio::time::interval(Duration::from_millis(500));
        
        loop {
            match self.refresh_pools().await {
                Ok(_) => break,
                Err(e) => {
                    if retries >= self.config.max_retries {
                        return Err(CoreError::AggregatorError(format!(
                            "Orca refresh failed after {} retries: {}",
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
                let (bid_depth, ask_depth) = self.calculate_depth(pool);
                let fee_multiplier = 1.0 - (pool.fee_rate as f64 / FEE_SCALE as f64);

                Some(UnifiedMarketData {
                    dex: DexType::Orca,
                    pool_address: pool.address,
                    base_mint: pool.token_mint_a,
                    quote_mint: pool.token_mint_b,
                    bid_price: price * fee_multiplier,
                    ask_price: price / fee_multiplier,
                    bid_size: bid_depth,
                    ask_size: ask_depth,
                    volume_24h: self.estimate_volume(pool),
                    liquidity: (bid_depth * price + ask_depth) / 2.0,
                    timestamp: chrono::Utc::now().timestamp(),
                })
            })
            .fold((0.0, 0.0, 0.0), |(b, a, l), data| {
                (b + data.bid_price, a + data.ask_price, l + data.liquidity)
            });

        Ok(UnifiedMarketData {
            dex: DexType::Orca,
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

impl OrcaClient {
    fn estimate_volume(&self, pool: &WhirlpoolState) -> f64 {
        // Estimate volume based on fee accumulation
        let fee_value = self.convert_amount(pool.protocol_fee as f64, pool.decimals_b);
        fee_value / (pool.fee_rate as f64 / FEE_SCALE as f64)
    }
}

impl From<OrcaError> for CoreError {
    fn from(e: OrcaError) -> Self {
        CoreError::AggregatorError(format!("Orca error: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::account::Account;

    fn mock_whirlpool_account() -> Account {
        let mut data = vec![0u8; 344];
        // Populate test data
        data[8..40].copy_from_slice(&[1u8; 32]);  // token_mint_a
        data[40..72].copy_from_slice(&[2u8; 32]); // token_mint_b
        data[72..74].copy_from_slice(&100u16.to_le_bytes()); // tick_spacing
        data[104..120].copy_from_slice(&1_000_000u128.to_le_bytes()); // liquidity
        data[120..136].copy_from_slice(&(2f64.sqrt() * 2f64.powi(64)).to_bits().to_le_bytes()); // sqrt_price
        data[144..146].copy_from_slice(&3000u16.to_le_bytes()); // fee_rate (0.3%)
        data[152..160].copy_from_slice(&100_000u64.to_le_bytes()); // protocol_fee
        data[168] = 6; // decimals_a
        data[169] = 6; // decimals_b
        Account { data, ..Account::default() }
    }

    #[tokio::test]
    async fn test_whirlpool_parsing() {
        let pubkey = Pubkey::new_unique();
        let account = mock_whirlpool_account();
        let pool = OrcaClient::parse_whirlpool_account(&pubkey, &account).unwrap();
        
        assert_eq!(pool.tick_spacing, 100);
        assert_eq!(pool.liquidity, 1_000_000);
        assert_eq!(pool.fee_rate, 3000);
    }

    #[tokio::test]
    async fn test_price_calculation() {
        let client = OrcaClient::new(Arc::new(RpcClient::new("test")), DexConfig::default()).unwrap();
        let mut pool = WhirlpoolState::default();
        pool.sqrt_price = (2f64.sqrt() * 2f64.powi(64)) as u128;
        pool.decimals_a = 6;
        pool.decimals_b = 6;
        
        let price = client.calculate_price(&pool).unwrap();
        assert!((price - 2.0).abs() < f64::EPSILON * 10.0);
    }
}
