use ring::aead::{Aead, Nonce, UnboundKey, AES_256_GCM};
use solana_sdk::signature::{Keypair, Signer};
use anyhow::Result;
use log::{info, error};

pub struct WalletManager {
    keypair: Keypair,
}

impl WalletManager {
    pub fn new() -> Self {
        Self { keypair: Keypair::new() }
    }

    pub fn encrypt_private_key(&self, key: &[u8]) -> Result<Vec<u8>> {
        let unbound_key = UnboundKey::new(&AES_256_GCM, key)?;
        let nonce = Nonce::try_assume_unique_for_key(&[0; 12])?;
        let mut in_out = self.keypair.to_bytes().to_vec();
        AES_256_GCM.seal_in_place_append_tag(unbound_key, nonce, &[], &mut in_out)?;
        info!("Private key encrypted");
        Ok(in_out)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let wallet = WalletManager::new();
    wallet.encrypt_private_key(&[0; 32])?;
    Ok(())
}
