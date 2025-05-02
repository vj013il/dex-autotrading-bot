import axios from 'axios';
import crypto from 'crypto';
import { encryptData } from '../utils/encryption.js';

export class BinanceAPI {
  constructor() {
    this.apiKey = decryptData(process.env.BINANCE_API_KEY);
    this.secret = decryptData(process.env.BINANCE_SECRET);
  }

  async getPrice(symbol) {
    const response = await axios.get(
      `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`
    );
    return parseFloat(response.data.price);
  }

  async createOrder(order) {
    const timestamp = Date.now();
    const query = `symbol=${order.symbol}&side=${order.side}&type=MARKET&quantity=${order.quantity}&timestamp=${timestamp}`;
    
    const signature = crypto
      .createHmac('sha256', this.secret)
      .update(query)
      .digest('hex');

    return axios.post(
      'https://api.binance.com/api/v3/order',
      `${query}&signature=${signature}`,
      { headers: { 'X-MBX-APIKEY': this.apiKey } }
    );
  }
}
