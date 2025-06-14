const { ethers } = require('ethers');
const { encrypt, decrypt } = require('../core/encryption');

class WalletManager {
  constructor(masterPassword) {
    this.wallets = [];
    this.masterPassword = masterPassword;
  }

  createWallet() {
    const wallet = ethers.Wallet.createRandom();
    const encryptedPrivateKey = encrypt(wallet.privateKey, this.masterPassword);
    this.wallets.push({ address: wallet.address, encryptedPrivateKey });
    return wallet.address;
  }

  getWallet(index) {
    const walletData = this.wallets[index];
    if (!walletData) throw new Error('Wallet not found');
    const privateKey = decrypt(walletData.encryptedPrivateKey, this.masterPassword);
    return new ethers.Wallet(privateKey, provider);
  }

  async initialize(masterPassword) {
    this.masterPassword = masterPassword;
    // Load existing wallets from storage (if any)
  }
}

module.exports = new WalletManager(process.env.MASTER_PASSWORD);
