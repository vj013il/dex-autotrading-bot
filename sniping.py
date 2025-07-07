import json
import requests
from decimal import Decimal
from websocket import create_connection
import time

# Trader parameters
BALANCE = 1_000_000  # USD
RISK_MIN = 0.10  # 10% min risk per trade
RISK_MAX = 0.50  # 50% max risk per trade
MAX_LEVERAGE = 20  # Max leverage
MIN_ORDER_SIZE = 10_000_000  # Min order size to snipe ($10M)
PAIRS = ["XRP/USDC", "BTC/USDC", "ETH/USDC", "SOL/USDC", "PEPE/USDC"]
LIQUIDATION_THRESHOLD = 0.025  # 2.5% margin threshold

# Fetch market data (price, volatility)
def get_market_data(symbol):
    api_url = "https://api.hyperliquid.xyz/market-data"
    try:
        response = requests.get(api_url, params={"symbol": symbol})
        data = response.json()
        return {
            "price": Decimal(str(data["price"])),
            "volatility": Decimal(str(data["volatility_24h"]))
        }
    except Exception:
        # Fallback data
        return {"price": Decimal("70000" if "BTC" in symbol else "0.7" if "XRP" in symbol else "2500" if "ETH" in symbol else "250" if "SOL" in symbol else "0.00001"), "volatility": Decimal("0.02")}

# Calculate position size based on risk and volatility
def calculate_position_size(balance, risk_percent, price, volatility):
    risk_amount = Decimal(str(balance)) * Decimal(str(risk_percent))
    stop_loss_distance = price * Decimal("0.02")  # 2% SL
    position_size = risk_amount / stop_loss_distance
    return position_size

# Calculate safe leverage
def calculate_safe_leverage(position_size, price, balance, volatility):
    position_value = position_size * price
    margin_required = position_value / Decimal(str(MAX_LEVERAGE))
    safe_leverage = min(
        MAX_LEVERAGE,
        (balance * Decimal("0.8")) / margin_required
    )
    if volatility > Decimal("0.03"):
        safe_leverage = min(safe_leverage, 10)
    elif volatility > Decimal("0.02"):
        safe_leverage = min(safe_leverage, 15)
    return safe_leverage

# Place order via REST API
def place_order(symbol, price, size, direction, leverage, order_type="limit"):
    api_url = "https://api.hyperliquid.xyz/order"
    payload = {
        "coin": symbol,
        "is_buy": direction == "buy",
        "size": float(size),
        "price": float(price),
        "leverage": leverage,
        "type": order_type
    }
    try:
        response = requests.post(api_url, json=payload, headers={"Authorization": "YOUR_API_KEY"})
        return response.json()
    except Exception as e:
        print(f"Order placement error: {e}")
        return None

# Sniper bot logic
def sniper_bot():
    ws_connections = {}
    for symbol in PAIRS:
        ws = create_connection("wss://api.hyperliquid.xyz/ws")
        ws.send(json.dumps({"method": "subscribe", "subscription": {"type": "orderbook", "coin": symbol}}))
        ws_connections[symbol] = ws

    while True:
        for symbol, ws in ws_connections.items():
            try:
                data = json.loads(ws.recv())
                if data["type"] == "orderbook":
                    market_data = get_market_data(symbol)
                    price = market_data["price"]
                    volatility = market_data["volatility"]

                    # Calculate risk based on volatility
                    risk_percent = RISK_MIN if volatility > Decimal("0.03") else RISK_MAX

                    for order in data["bids"] + data["asks"]:
                        order_value = float(order["size"]) * float(order["price"])
                        if order_value > MIN_ORDER_SIZE:
                            direction = "buy" if order in data["bids"] else "sell"
                            front_run_price = float(order["price"]) * (1.001 if direction == "buy" else 0.999)
                            
                            # Calculate position
                            position_size = calculate_position_size(BALANCE, risk_percent, price, volatility)
                            leverage = calculate_safe_leverage(position_size, price, BALANCE, volatility)
                            
                            # Place front-running order
                            order_result = place_order(symbol, front_run_price, position_size, direction, leverage)
                            
                            # Set SL/TP
                            stop_loss_price = front_run_price * (0.98 if direction == "buy" else 1.02)
                            take_profit_price = front_run_price * (1.03 if direction == "buy" else 0.97)
                            
                            print(f"Snipe: {direction} {position_size:.4f} {symbol} at {front_run_price:.2f}, SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}")
                            
            except Exception as e:
                print(f"WebSocket error for {symbol}: {e}")
                # Reconnect WebSocket
                ws_connections[symbol] = create_connection("wss://api.hyperliquid.xyz/ws")
                ws_connections[symbol].send(json.dumps({"method": "subscribe", "subscription": {"type": "orderbook", "coin": symbol}}))
        
        time.sleep(0.1)  # Prevent CPU overload

if __name__ == "__main__":
    sniper_bot()
