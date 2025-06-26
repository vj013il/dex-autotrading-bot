import asyncio
from web3 import Web3
from utils.config import load_config

class MempoolMonitor:
    def __init__(self):
        self.config = load_config()
        self.w3 = Web3(Web3.WebsocketProvider(self.config['rpc_url']))

    async def monitor_mempool(self, token_address):
        """Monitor mempool for new token pair transactions."""
        while True:
            pending_txs = self.w3.eth.get_block('pending').transactions
            for tx in pending_txs:
                if token_address.lower() in tx.get('input', '').lower():
                    print(f"Detected transaction for {token_address}: {tx['hash'].hex()}")
            await asyncio.sleep(0.1)  # Poll every 100ms

if __name__ == "__main__":
    monitor = MempoolMonitor()
    asyncio.run(monitor.monitor_mempool("0xTokenAddress"))
