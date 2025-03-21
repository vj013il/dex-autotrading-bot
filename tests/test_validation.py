import pytest
from src.validator.core import CryptoValidator

test_cases = [
    ("BTC", "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2", True),
    ("BTC", "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", True),
    ("ETH", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", True),
    ("ETH", "0x742d35cc6634c0532925a3b844bc454e4438f44e", False),  # Invalid checksum
]

@pytest.mark.parametrize("currency,address,expected", test_cases)
def test_address_validation(currency, address, expected):
    assert CryptoValidator.validate(currency, address) == expected
