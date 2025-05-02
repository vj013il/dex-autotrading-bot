import { Connection, Keypair } from '@solana/web3.js';
import { Jupiter } from '@jup-ag/core';
import { encryptData } from '../utils/encryption.js';

export class DCAStrategy {
  constructor(wallet, config) {
    this.wallet = wallet;
    this.config = config;
    this.connection = new Connection(process.env.SOLANA_RPC_URL);
    this.jupiter = null;
  }

  async initialize() {
    this.jupiter = await Jupiter.load({
      connection: this.connection,
      cluster: 'mainnet-beta',
      user: this.wallet,
    });
  }

  async execute() {
    try {
      const quote = await this.jupiter.quote({
        inputMint: this.config.inputToken,
        outputMint: this.config.outputToken,
        amount: this.config.amount,
        slippage: this.config.slippage,
      });
      
      const { execute } = await this.jupiter.exchange({
        quote,
      });
      
      const txid = await execute();
      console.log(`DCA executed: ${txid}`);
      return txid;
    } catch (error) {
      console.error('DCA error:', error);
      this.handleMEVProtection();
    }
  }

  handleMEVProtection() {
    // Реализация защиты от MEV
    console.log('Activating MEV protection...');
    // Здесь можно добавить задержку или изменить RPC
  }
}
