import { Connection, Keypair } from '@solana/web3.js';
import { Jupiter } from '@jup-ag/core';

export class JupiterAPI {
  constructor() {
    this.connection = new Connection(process.env.SOLANA_RPC_URL);
  }

  async getPrice(pair) {
    const jupiter = await Jupiter.load({
      connection: this.connection,
      cluster: 'mainnet-beta'
    });
    
    const quote = await jupiter.quote({
      inputMint: pair.baseMint,
      outputMint: pair.quoteMint,
      amount: 1 * 10 ** pair.baseDecimals,
      slippage: 0.5
    });
    
    return quote.outputAmount / 10 ** pair.quoteDecimals;
  }
}
