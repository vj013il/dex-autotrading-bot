import axios from 'axios';
import { Jupiter } from '@jup-ag/core';
import { BinanceAPI } from '../api/binance.js';

export class ArbitrageStrategy {
  constructor() {
    this.binance = new BinanceAPI();
    this.jupiter = new Jupiter();
    this.minSpread = 0.008; // 0.8%
  }

  async checkOpportunity(pair) {
    const [dexPrice, cexPrice] = await Promise.all([
      this.jupiter.getPrice(pair),
      this.binance.getPrice(pair)
    ]);

    const spread = (cexPrice - dexPrice) / dexPrice;
    
    if (spread > this.minSpread) {
      return {
        buyOn: 'DEX',
        sellOn: 'CEX',
        profit: spread
      };
    }
    
    return null;
  }

  async executeArbitrage(opportunity) {
    // Realization of the arbitration transaction
  }
}
