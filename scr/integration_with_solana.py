from solders.keypair import Keypair
from solana.rpc.api import Client

class WalletClient:
    def __init__(self, private_key):
        self.keypair = Keypair.from_base58_string(private_key)
        self.conn = Client("https://api.mainnet-beta.solana.com")

    def sign_transaction(self, transaction):
        return transaction.sign(self.keypair)

    def send_transaction(self, signed_tx):
        return self.conn.send_raw_transaction(signed_tx)
