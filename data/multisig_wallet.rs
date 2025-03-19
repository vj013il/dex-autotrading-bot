use squads_mpl::{Multisig, instruction::create_transaction};

async fn create_multisig_tx(
    multisig_pda: &Pubkey,
    creator: &Keypair,
    signers: Vec<Pubkey>,
    threshold: u8,
) -> Result<()> {
    let multisig = Multisig::new(creator.pubkey(), signers, threshold);
    let tx_ix = create_transaction(
        multisig_pda,
        &creator.pubkey(),
        vec![system_instruction::transfer(
            &multisig_pda,
            &recipient,
            amount,
        )],
    )?;

    let tx = Transaction::new_signed_with_payer(
        &[tx_ix],
        Some(&creator.pubkey()),
        &[creator],
        recent_blockhash,
    );

    // Requires signatures from `threshold` participants
    rpc_client.send_transaction(&tx).await?;
    Ok(())
}
