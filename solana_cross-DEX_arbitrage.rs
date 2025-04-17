use solana_client::nonblocking::rpc_client::RpcClient;
use solana_sdk::{pubkey::Pubkey, signature::Keypair};
use jito_protos::packet::Packet;
use crate::{dex::{Raydium, Orca, PumpFun}, risk::RiskValidator};

const MIN_PROFIT_BPS: u64 = 80; // 0.8%
const MAX_SLIPPAGE_BPS: u64 = 150; // 1.5%

pub struct ArbitrageEngine {
    raydium: Raydium,
    orca: Orca,
    pumpfun: PumpFun,
    risk_validator: RiskValidator,
    jito_client: JitoClient,
}

impl ArbitrageEngine {
    pub async fn find_and_execute_arbitrage(&self) -> Result<(), StrategyError> {
        // 1. Get real-time prices
        let (raydium_price, raydium_liquidity) = self.raydium.get_price("SOL/USDC").await?;
        let (orca_price, orca_liquidity) = self.orca.get_price("SOL/USDC").await?;
        
        // 2. Calculate potential profit
        let (buy_price, sell_price, dex_pair) = self.find_best_spread(
            raydium_price, 
            orca_price,
            raydium_liquidity,
            orca_liquidity
        )?;

        // 3. Risk validation
        let base_amount = self.calculate_position_size(buy_price);
        self.risk_validator.validate_arbitrage(
            base_amount,
            buy_price,
            sell_price
        )?;

        // 4. Build Jito bundle
        let bundle = self.build_arbitrage_bundle(
            dex_pair,
            base_amount,
            buy_price,
            sell_price
        )?;

        // 5. Execute with MEV protection
        let signature = self.jito_client.send_bundle(bundle).await?;
        Ok(())
    }

    fn find_best_spread(
        &self,
        price_a: f64,
        price_b: f64,
        liq_a: f64,
        liq_b: f64
    ) -> Result<(f64, f64, DexPair), StrategyError> {
        // Complex price comparison logic with liquidity adjustment
        let spread = (price_a - price_b).abs();
        let adjusted_spread = spread * (liq_a.min(liq_b) / 1_000_000.0).sqrt();
        
        if adjusted_spread < MIN_PROFIT_BPS as f64 / 10000.0 {
            return Err(StrategyError::NoArbitrageOpportunity);
        }

        match price_a > price_b {
            true => Ok((price_b, price_a, DexPair::OrcaRaydium)),
            false => Ok((price_a, price_b, DexPair::RaydiumOrca)),
        }
    }
}
