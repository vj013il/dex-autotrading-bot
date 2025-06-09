use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    pubkey::Pubkey,
    signature::{Keypair, Signer},
    transaction::Transaction,
};
use std::env;
use std::str::FromStr;

const JUPITER_API_URL: &str = "https://api.jup.ag/swap";

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Loading environment variables
    dotenv::dotenv().ok();
    let rpc_url = env::var("SOLANA_RPC_URL").expect("SOLANA_RPC_URL must be set");
    let private_key = env::var("SOLANA_PRIVATE_KEY").expect("SOLANA_PRIVATE_KEY must be set");

    // Initializing a Solana client
    let client = RpcClient::new(rpc_url);

    // Loading a key pair
    let keypair = Keypair::from_base58_string(&private_key);
    let wallet_pubkey = keypair.pubkey();

    println!("Wallet: {}", wallet_pubkey);

    // Example: swap execution via Jupiter
    let token_in = "So11111111111111111111111111111111111111112"; // WSOL
    let token_out = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"; // USDC
    let amount = 1000000; // 0.001 SOL в lamports

    // Request for Jupiter API
    let swap_instruction = get_swap_instruction(token_in, token_out, amount, &wallet_pubkey)?;

    // Creating and sending a transaction
    let recent_blockhash = client.get_latest_blockhash()?;
    let transaction = Transaction::new_signed_with_payer(
        &[swap_instruction],
        Some(&wallet_pubkey),
        &[&keypair],
        recent_blockhash,
    );

    let signature = client.send_and_confirm_transaction(&transaction)?;
    println!("Swap executed: {}", signature);

    Ok(())
}

fn get_swap_instruction(
    token_in: &str,
    token_out: &str,
    amount: u64,
    wallet: &Pubkey,
) -> Result<solana_sdk::instruction::Instruction, Box<dyn std::error::Error>> {
    // Here will be an HTTP request to the Jupiter API
    println!(
        "Fetching swap instruction for {} -> {}, amount: {}, wallet: {}",
        token_in, token_out, amount, wallet
    );
    // Example of instructions
    Ok(solana_sdk::instruction::Instruction {
        program_id: Pubkey::from_str("JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB")?,
        accounts: vec![],
        data: vec![],
    })
}
