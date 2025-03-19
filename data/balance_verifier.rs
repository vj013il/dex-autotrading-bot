use anchor_lang::prelude::*;
use pyth_client::{AccountInfo, Price, PriceStatus};

#[program]
pub mod whale_guard {
    use super::*;

    pub fn verify_balance(ctx: Context<VerifyBalance>) -> Result<()> {
        let pyth_price_acc = &ctx.accounts.pyth_price_account;
        let price_data = pyth_client::load_price(pyth_price_acc).unwrap();

        // Checking price relevance
        require!(
            price_data.status == PriceStatus::Trading,
            ErrorCode::StalePrice
        );

        let sol_balance = ctx.accounts.user.lamports() as f64 / 1e9; // SOL -> decimals
        let usd_balance = sol_balance * price_data.price as f64;

        // Minimum balance $10k
        require!(usd_balance >= 10_000.0, ErrorCode::InsufficientBalance);

        Ok(())
    }
}

#[derive(Accounts)]
pub struct VerifyBalance<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    /// CHECK: Pyth price account для SOL/USD
    pub pyth_price_account: AccountInfo<'info>,
}
