#[cfg(test)]
mod tests {
    use super::*;
    use anchor_lang::solana_program::{clock::Clock, sysvar::Sysvar};
    use solana_program_test::*;
    use solana_sdk::{signature::Keypair, signer::Signer};

    #[tokio::test]
    async fn test_balance_verifier_sufficient() {
        // Setup Pyth price account with $100 SOL price
        let mut test = ProgramTest::new("whale_guard", id(), processor!(process_instruction));
        let pyth_price = create_pyth_price(100.0);
        
        let (mut banks_client, payer, recent_blockhash) = test.start().await;
        let user = Keypair::new();
        
        // Fund user with 101 SOL (101 * $100 = $10,100)
        fund_account(&mut banks_client, &user.pubkey(), 101_000_000_000).await;

        let mut tx = Transaction::new_with_payer(
            &[verify_balance_ix(user.pubkey(), pyth_price.pubkey())],
            Some(&payer.pubkey()),
        );
        tx.sign(&[&payer, &user], recent_blockhash);
        banks_client.process_transaction(tx).await.unwrap();
    }

    #[tokio::test]
    #[should_panic(expected = "InsufficientBalance")]
    async fn test_balance_verifier_insufficient() {
        let mut test = ProgramTest::new(...);
        let pyth_price = create_pyth_price(99.0); // 100 SOL = $9,900
        // ... similarly, but expect an error
    }

    #[tokio::test]
    #[should_panic(expected = "StalePrice")]
    async fn test_stale_price_data() {
        let mut pyth_price = create_pyth_price(100.0);
        pyth_price.status = PriceStatus::Unknown;
        // ...
    }

    #[tokio::test]
    async fn test_otc_init() {
        let buyer = Keypair::new();
        let seller = Keypair::new();
        let mint = create_spl_token(&mut test).await;

        let tx = init_otc_deal(&buyer, &seller, 1000, mint.pubkey()).await;
        let escrow = get_account_data::<OTCEscrow>(...).await;
        
        assert_eq!(escrow.amount, 1000);
        assert!(!escrow.is_completed);
    }

    #[tokio::test]
    async fn test_otc_confirm_success() {
        // Init deal
        // Fund escrow vault
        // Confirm with both parties
        let tx = confirm_otc(&buyer, &seller).await;
        let escrow = get_account_data(...).await;
        
        assert!(escrow.is_completed);
        assert_eq!(get_token_balance(vault).await, 0);
    }

    #[tokio::test]
    #[should_panic(expected = "MissingRequiredSignature")]
    async fn test_otc_confirm_unauthorized() {
        // Attempting to confirm the transaction with a third party
        let attacker = Keypair::new();
        let tx = confirm_otc(&attacker, &seller).await;
    }

    #[tokio::test]
    #[should_panic(expected = "DealCompleted")]
    async fn test_otc_double_confirm() {
        // Re-confirmation of an already completed transaction
    }

    #[tokio::test]
    async fn test_multisig_create() {
        let signers = vec![Keypair::new(), Keypair::new(), Keypair::new()];
        let threshold = 2;
        
        let tx = create_multisig(&signers[0], signers.iter().map(|k| k.pubkey()), threshold).await;
        let ms_account = get_account_data::<Multisig>(...).await;
        
        assert_eq!(ms_account.threshold, 2);
        assert_eq!(ms_account.signers.len(), 3);
    }

    #[tokio::test]
    async fn test_multisig_approve() {
        // Create transaction
        // Two of the participants confirm
        let tx = approve_tx(&signer1).await;
        let tx = approve_tx(&signer2).await;
        
        let tx_state = get_tx_state(...).await;
        assert!(tx_state.executed);
    }

    #[tokio::test]
    #[should_panic(expected = "ThresholdNotMet")]
    async fn test_multisig_insufficient_approvals() {
        // Только 1 подтверждение из 2 требуемых
    }

    // Tests for TWAP strategy
    #[tokio::test]
    async fn test_twap_split_orders() {
        let total = 100_000;
        let chunks = execute_twap_split(total, 100).await;
        
        assert_eq!(chunks.len(), 100);
        assert_eq!(chunks.iter().sum::<u64>(), total);
    }

    #[tokio::test]
    async fn test_twap_price_slippage() {
        // Simulate price change between chunks
        let result = execute_twap_with_slippage().await;
        assert!(result.avg_price <= max_allowed_slippage);
    }

    // Safety tests
    #[tokio::test]
    #[should_panic(expected = "InvalidPriceAccount")]
    async fn test_fake_pyth_account() {
        // Передача поддельного Pyth-аккаунта
    }

    #[tokio::test]
    async fn test_zk_proof_verification() {
        // Verification without address disclosure
        let proof = generate_zk_proof(user, 10_000).await;
        let is_valid = verify_zk_proof(proof).await;
        assert!(is_valid);
    }

    // Events tests (Events)
    #[tokio::test]
    async fn test_emit_balance_alert() {
        let logs = trigger_balance_alert(9_000).await;
        assert!(logs.contains("BalanceAlert { amount: 9000 }"));
    }

    // Интеграционные тесты
    #[tokio::test]
    async fn test_full_otc_flow() {
        // Полный цикл: Init -> Fund -> Confirm -> Check Balances
        let initial_balance = get_balance(seller).await;
        // ... выполнение всей OTC-сделки
        let final_balance = get_balance(seller).await;
        assert_eq!(final_balance, initial_balance + 1000);
    }

    #[tokio::test]
    async fn test_multisig_recovery() {
        // Single key loss simulation
        let new_signer = Keypair::new();
        let tx = update_multisig_signers([...], new_signer.pubkey()).await;
        // ...
    }

    // Boundary value tests
    #[tokio::test]
    async fn test_max_balance() {
        // 1B SOL * $100 = $100B
        fund_account(user, 1_000_000_000 * 1e9).await;
        // Должно пройти без ошибок
    }

    #[tokio::test]
    #[should_panic(expected = "Overflow")]
    async fn test_balance_overflow() {
        // Attempting to deposit more than u64::MAX
    }
}

// Auxiliary functions
async fn fund_account(banks_client: &mut BanksClient, account: &Pubkey, lamports: u64) {
    // ... Realization of account financing
}

fn create_pyth_price(price: f64) -> AccountInfo {
    // ... Generating a test Pyth account
}
