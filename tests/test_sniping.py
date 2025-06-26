import unittest
from core.sniping import Sniper

class TestSniper(unittest.TestCase):
    def setUp(self):
        self.sniper = Sniper()

    def test_snipe_token(self):
        token_address = "0xMockTokenAddress"
        tx_hash = self.sniper.snipe_token(token_address, 0.1)
        self.assertIsNotNone(tx_hash, "Transaction hash should not be None")

if __name__ == "__main__":
    unittest.main()
