// lib.rs (Solana Program)
use anchor_lang::prelude::*;
use pyth_client::Price;

declare_id!("YourProgramIDHere");

#[program]
pub mod solana_mm_pro {
    use super::*;

    // Initialize strategy account
    pub fn initialize_strategy(
        ctx: Context<InitializeStrategy>,
        spread_bps: u16, // 0.01% increments (e.g., 50 = 0.5%)
        max_leverage: u8,
    ) -> Result<()> {
        let strategy = &mut ctx.accounts.strategy;
        strategy.owner = *ctx.accounts.owner.key;
        strategy.spread_bps = spread_bps;
        strategy.max_leverage = max_leverage;
        strategy.active = true;
        Ok(())
    }

    // Update orders based on Pyth price
    pub fn update_orders(ctx: Context<UpdateOrders>, price: Price) -> Result<()> {
        let strategy = &ctx.accounts.strategy;
        
        // Calculate bid/ask with spread
        let mid_price = price.get_price() as f64;
        let spread = (mid_price * (strategy.spread_bps as f64)) / 10_000.0;
        
        // Place orders on Raydium/Orca
        let bid_price = mid_price - spread;
        let ask_price = mid_price + spread;
        
        // CPI call to Raydium
        place_order_on_dex(
            bid_price,
            ask_price,
            ctx.accounts.amm_program.clone(),
        )?;
        
        Ok(())
    }
}

// Accounts for initialize_strategy
#[derive(Accounts)]
pub struct InitializeStrategy<'info> {
    #[account(init, payer = owner, space = 64)]
    pub strategy: Account<'info, Strategy>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

// Strategy account structure
#[account]
pub struct Strategy {
    pub owner: Pubkey,
    pub spread_bps: u16, 
    pub max_leverage: u8,
    pub active: bool,
}
