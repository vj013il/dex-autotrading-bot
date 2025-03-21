import re
from bech32 import bech32_decode
from hashlib import sha3_256

class CryptoValidator:
    @staticmethod
    def validate(currency: str, address: str) -> bool:
        """
        Validates cryptocurrency address against blockchain standards
        
        Args:
            currency (str): Cryptocurrency ticker (BTC, ETH, etc)
            address (str): Wallet address to validate
            
        Returns:
            bool: True if address is valid
        """
        try:
            if currency == "BTC":
                return CryptoValidator._validate_btc(address)
            elif currency == "ETH":
                return CryptoValidator._validate_eth(address)
            # Add other currencies here
            else:
                raise ValueError(f"Unsupported currency: {currency}")
        except Exception as e:
            # Logging errors for further analysis
            print(f"Validation error: {str(e)}")
            return False

    @staticmethod
    def _validate_btc(address: str) -> bool:
        # Verification for Bitcoin (P2PKH/P2SH/Bech32)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        elif re.match(r'^(bc1)[a-zA-HJ-NP-Z0-9]{25,90}$', address):
            hrp, _ = bech32_decode(address)
            return hrp == 'bc'
        return False

    @staticmethod
    def _validate_eth(address: str) -> bool:
        # Ethereum checksum verification (EIP-55)
        if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
            return False
            
        checksum = sha3_256(address[2:].lower().encode()).hexdigest()
        for i in range(2, 42):
            if (int(checksum[i-2], 16) >= 8 and 
                address[i].upper() != address[i]):
                return False
            elif (int(checksum[i-2], 16) < 8 and 
                address[i].lower() != address[i]):
                return False
        return True
