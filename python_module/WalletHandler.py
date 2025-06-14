import asyncio
import platform
import hashlib
import base64
from web3 import Account

class WalletHandler:
    def __init__(self):
        self.wallets = []
        self.master_password = None

    async def generate_wallet(self):
        await asyncio.sleep(0.1) 
        private_key = Account.create().privateKey.hex()
        address = Account.from_key(private_key).address
        encrypted_key = self._encrypt_private_key(private_key, "master_pass") 
        wallet = {"address": address, "encrypted_key": encrypted_key, "balance": 0}
        self.wallets.append(wallet)
        return wallet

    def _encrypt_private_key(self, private_key, password):
        key = hashlib.sha256(password.encode()).digest()
        encrypted = base64.b64encode(key + private_key.encode()).decode()
        return encrypted

    async def distribute_capital(self, total_capital, allocation_percent):
        allocation = (float(allocation_percent) / 100) * total_capital / len(self.wallets) if self.wallets else 0
        for wallet in self.wallets:
            wallet["balance"] = allocation
        return self.wallets

if platform.system() == "Emscripten":
    asyncio.ensure_future(WalletHandler().generate_wallet())
