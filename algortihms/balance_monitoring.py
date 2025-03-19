import websockets
import json
from helius import Helius

async def balance_monitor(wallet: str, min_balance_usd: float):
    helius = Helius(api_key="YOUR_API_KEY")
    
    async with websockets.connect(helius.websocket_url) as ws:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "accountSubscribe",
            "params": [wallet, {"encoding": "jsonParsed"}]
        }))
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            
            if 'result' in data:
                balance_lamports = data['result']['value']['lamports']
                balance_sol = balance_lamports / 1e9
                usd_value = await get_sol_price() * balance_sol
                
                if usd_value < min_balance_usd:
                    send_alert(f"Low balance: ${usd_value:,.2f}")

async def get_sol_price():
    # Integration with Pyth Network
    async with AsyncClient("https://pyth-api-url") as client:
        resp = await client.get_account_info(Pubkey.from_string("SOL_USD_PYTH_ACCOUNT"))
        price_data = parse_price_data(resp.value.data)
        return price_data.price
