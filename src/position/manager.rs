use solana_sdk::{pubkey::Pubkey, signature::Signature};
use std::{
    collections::{HashMap, HashSet},
    sync::Arc,
    time::{Duration, Instant},
};
use tokio::{
    sync::{RwLock, Mutex},
    time::interval
};
use crate::{
    core::{CoreError, DexType, UnifiedMarketData},
    data_aggregator::DataAggregator,
    risk::{RiskManager, RiskApproval},
    strategy::allocator::CapitalAllocator,
};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub token: Pubkey,
    pub size: f64,          // In token units
    pub entry_price: f64,   // In quote currency (e.g., USD)
    pub value: f64,         // Current market value
    pub liquidity_tier: u8, // 1-5 based on liquidity
    pub last_updated: Instant,
}

#[derive(Debug, Clone)]
pub struct PositionConfig {
    pub max_single_allocation: f64,    // 0.1 for 10%
    pub rebalance_interval: Duration,  // 6 hours
    pub min_liquidity: f64,            // $50k
    pub slippage_tolerance: f64,       // 0.015 for 1.5%
}

pub struct PositionManager {
    positions: Arc<RwLock<HashMap<Pubkey, Position>>>,
    config: PositionConfig,
    data_aggregator: Arc<DataAggregator>,
    risk_manager: Arc<RiskManager>,
    allocator: Arc<CapitalAllocator>,
    rebalance_lock: Mutex<()>,
}

impl PositionManager {
    pub fn new(
        config: PositionConfig,
        data_aggregator: Arc<DataAggregator>,
        risk_manager: Arc<RiskManager>,
        allocator: Arc<CapitalAllocator>,
    ) -> Self {
        let manager = Self {
            positions: Arc::new(RwLock::new(HashMap::new())),
            config,
            data_aggregator,
            risk_manager,
            allocator,
            rebalance_lock: Mutex::new(()),
        };

        // Start background tasks
        tokio::spawn(manager.clone().rebalance_task());
        tokio::spawn(manager.clone().liquidity_monitor());

        manager
    }

    /// Main entry point for position updates
    pub async fn update_position(
        &self,
        token: Pubkey,
        delta: f64,
        price: f64,
    ) -> Result<(), CoreError> {
        let mut positions = self.positions.write().await;
        let current = positions.entry(token).or_insert(Position {
            token,
            size: 0.0,
            entry_price: price,
            value: 0.0,
            liquidity_tier: 0,
            last_updated: Instant::now(),
        });

        // Calculate new position size
        let new_size = current.size + delta;
        let new_value = new_size * price;

        // Check allocation limits
        self.check_allocation(token, new_value).await?;

        // Update position state
        current.size = new_size;
        current.value = new_value;
        current.last_updated = Instant::now();

        // Refresh liquidity tier
        current.liquidity_tier = self.calculate_liquidity_tier(token).await?;

        Ok(())
    }

    /// Core allocation check logic
    async fn check_allocation(&self, token: Pubkey, new_value: f64) -> Result<(), CoreError> {
        let total_assets = self.allocator.total_assets().await;
        let max_allowed = total_assets * self.config.max_single_allocation;

        if new_value > max_allowed {
            return Err(CoreError::PositionError(format!(
                "Allocation exceeded for {}: {:.2} > {:.2}",
                token, new_value, max_allowed
            )));
        }

        // Check against risk limits
        let risk_approval = self.risk_manager
            .validate_position_change(token, new_value)
            .await?;

        if !risk_approval.allowed {
            return Err(CoreError::PositionError(
                risk_approval.reason.unwrap_or_default()
            ));
        }

        Ok(())
    }

    /// Automated rebalancing task
    async fn rebalance_task(self: Arc<Self>) {
        let mut interval = interval(self.config.rebalance_interval);
        
        loop {
            interval.tick().await;
            
            // Prevent concurrent rebalances
            let _guard = self.rebalance_lock.lock().await;
            
            match self.execute_rebalance().await {
                Ok(_) => log::info!("Portfolio rebalanced successfully"),
                Err(e) => log::error!("Rebalance failed: {}", e),
            }
        }
    }

    /// Full portfolio rebalancing
    async fn execute_rebalance(&self) -> Result<(), CoreError> {
        let mut positions = self.positions.write().await;
        let total_assets = self.allocator.total_assets().await;
        let mut targets = self.allocator.calculate_targets().await?;

        // Liquidate over-allocated positions
        for (token, position) in positions.iter_mut() {
            let target = targets.get(token).copied().unwrap_or(0.0);
            let current_alloc = position.value / total_assets;
            
            if current_alloc > target {
                let reduce_by = (current_alloc - target) * total_assets;
                self.liquidate_partial(token, reduce_by, position).await?;
            }
        }

        // Allocate to underweight positions
        for (token, target) in targets {
            if !positions.contains_key(&token) {
                self.establish_position(token, target * total_assets).await?;
            }
        }

        Ok(())
    }

    /// Liquidity monitoring task
    async fn liquidity_monitor(self: Arc<Self>) {
        let mut interval = interval(Duration::from_secs(300)); // 5 minutes
        
        loop {
            interval.tick().await;
            
            let mut positions = self.positions.write().await;
            for (token, position) in positions.iter_mut() {
                match self.calculate_liquidity_tier(*token).await {
                    Ok(tier) => position.liquidity_tier = tier,
                    Err(e) => log::warn!("Liquidity check failed for {}: {}", token, e),
                }
            }
        }
    }

    /// Calculate liquidity tier based on market data
    async fn calculate_liquidity_tier(&self, token: Pubkey) -> Result<u8, CoreError> {
        let market_data = self.data_aggregator
            .get_token_data(token)
            .await
            .ok_or(CoreError::DataError("Token not found".into()))?;

        Ok(match market_data.liquidity {
            x if x >= 10_000_000.0 => 5,   // Tier 1: >$10M
            x if x >= 1_000_000.0 => 4,    // Tier 2: $1M-$10M
            x if x >= 500_000.0 => 3,      // Tier 3: $500k-$1M
            x if x >= 100_000.0 => 2,      // Tier 4: $100k-$500k
            _ => 1,                        // Tier 5: <$100k
        })
    }
}

// Integration with trading execution
impl PositionManager {
    async fn liquidate_partial(
        &self,
        token: &Pubkey,
        amount: f64,
        position: &mut Position,
    ) -> Result<(), CoreError> {
        let price = self.data_aggregator
            .get_price(*token)
            .await
            .ok_or(CoreError::DataError("Price unavailable".into()))?;

        let size_to_sell = amount / price;
        let slippage = self.calculate_slippage(*token, size_to_sell).await?;

        if slippage > self.config.slippage_tolerance {
            return Err(CoreError::SlippageError(
                format!("Slippage {:.2}% exceeds tolerance", slippage * 100.0)
            ));
        }

        // Execute TWAP order through strategy engine
        self.allocator.execute_twap(
            *token,
            size_to_sell,
            Duration::from_secs(300), // 5 minute TWAP
            self.config.slippage_tolerance
        ).await?;

        // Update position
        position.size -= size_to_sell;
        position.value = position.size * price;
        position.last_updated = Instant::now();

        Ok(())
    }

    async fn establish_position(
        &self,
        token: Pubkey,
        target_value: f64,
    ) -> Result<(), CoreError> {
        let price = self.data_aggregator
            .get_price(token)
            .await
            .ok_or(CoreError::DataError("Price unavailable".into()))?;

        let size_to_buy = target_value / price;
        let slippage = self.calculate_slippage(token, size_to_buy).await?;

        if slippage > self.config.slippage_tolerance {
            return Err(CoreError::SlippageError(
                format!("Slippage {:.2}% exceeds tolerance", slippage * 100.0)
            ));
        }

        // Execute TWAP order
        self.allocator.execute_twap(
            token,
            size_to_buy,
            Duration::from_secs(300),
            self.config.slippage_tolerance
        ).await?;

        // Add new position
        self.update_position(token, size_to_buy, price).await?;

        Ok(())
    }

    async fn calculate_slippage(&self, token: Pubkey, size: f64) -> Result<f64, CoreError> {
        // Get order book depth from aggregator
        let depth = self.data_aggregator
            .get_market_depth(token)
            .await
            .ok_or(CoreError::DataError("Depth unavailable".into()))?;

        // Simulate market impact
        let slippage = depth.estimate_slippage(size);
        Ok(slippage)
    }
}

// Clone implementation for background tasks
impl Clone for PositionManager {
    fn clone(&self) -> Self {
        Self {
            positions: self.positions.clone(),
            config: self.config.clone(),
            data_aggregator: self.data_aggregator.clone(),
            risk_manager: self.risk_manager.clone(),
            allocator: self.allocator.clone(),
            rebalance_lock: Mutex::new(()),
        }
    }
}
