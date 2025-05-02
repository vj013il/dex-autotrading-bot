import { Connection } from '@solana/web3.js';

export class MEVProtector {
  static async sendBundle(transactions, rpcUrls) {
    // Sending transactions through several RPCs
    const promises = rpcUrls.map(url => {
      const conn = new Connection(url);
      return Promise.all(
        transactions.map(tx => conn.sendRawTransaction(tx))
      );
    });
    
    return Promise.any(promises);
  }

  static splitOrder(amount, chunks = 3) {
    // Splitting the warrant
    const chunkSize = amount / chunks;
    return Array(chunks).fill(chunkSize);
  }
}
