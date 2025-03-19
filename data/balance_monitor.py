from helius import Helius
import websockets

async def monitor_balance(wallet: str, min_balance: float):
    async with websockets.connect(f"wss://helius.io/ws?api-key=YOUR_KEY") as ws:
        await ws.send(json.dumps({
            "action": "subscribe",
            "addresses": [wallet]
        }))
        
        async for msg in ws:
            data = json.loads(msg)
            balance = data['balance'] / 1e9  # SOL
            if balance < min_balance:
                send_alert(f"Balance below ${min_balance}: {balance} SOL")

def send_alert(message: str):
    # Integration with Telegram/Email
    print(f"ALERT: {message}")
