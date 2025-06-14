import asyncio
import platform
from datetime import datetime

class TransactionLogger:
    def __init__(self):
        self.logs = []

    async def log_transaction(self, tx_data):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - TX: {tx_data.get('tx_hash', 'N/A')} - Profit: ${tx_data.get('profit', 0):.2f}"
        self.logs.append(log_entry)
        return log_entry

    async def get_logs(self):
        await asyncio.sleep(0.1)
        return self.logs

if platform.system() == "Emscripten":
    asyncio.ensure_future(TransactionLogger().log_transaction({"tx_hash": "0x123", "profit": 100.0}))
