#[program]
pub mod otc_escrow {
    use super::*;

    pub fn init_deal(ctx: Context<InitOTC>, amount: u64, token_mint: Pubkey) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        escrow.buyer = ctx.accounts.buyer.key();
        escrow.seller = ctx.accounts.seller.key();
        escrow.amount = amount;
        escrow.token_mint = token_mint;
        escrow.is_completed = false;
        Ok(())
    }

    // Confirmation of the transaction with 2/2 signatures
    pub fn confirm_deal(ctx: Context<ConfirmOTC>) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        require!(!escrow.is_completed, ErrorCode::DealCompleted);

        // Transfer tokens from escrow to buyer
        let transfer_ix = spl_token::instruction::transfer(
            &spl_token::id(),
            &escrow.vault.key(),
            &escrow.buyer.key(),
            &escrow.authority.key(),
            &[],
            escrow.amount,
        )?;
        invoke(&transfer_ix, &[escrow.vault.to_account_info()])?;

        escrow.is_completed = true;
        Ok(())
    }
}

#[account]
pub struct OTCEscrow {
    pub buyer: Pubkey,
    pub seller: Pubkey,
    pub amount: u64,
    pub token_mint: Pubkey,
    pub is_completed: bool,
}
