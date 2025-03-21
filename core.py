import re
from hashlib import sha256, sha3_256
from bech32 import bech32_decode, convertbits

class CryptoValidator:
    
    @staticmethod
    def validate(currency: str, address: str) -> bool:
        """Basic validation function for all supported cryptocurrencies"""
        currency = currency.upper()
        address = address.strip()
        
        if currency == "BTC":
            return CryptoValidator._validate_btc(address)
        elif currency == "ETH":
            return CryptoValidator._validate_eth(address)
        elif currency == "LTC":
            return CryptoValidator._validate_ltc(address)
        elif currency == "BNB":
            return CryptoValidator._validate_bnb(address)
        else:
            raise ValueError(f"Unsupported currency: {currency}")

    @staticmethod
    def _validate_btc(address: str) -> bool:
        """Bitcoin: P2PKH, P2SH, Bech32 и Bech32m"""
        # Basic checks
        if len(address) < 26 or len(address) > 90:
            return False
        
        # Bech32 (SegWit) verification
        if address.startswith('bc1') or address.startswith('tb1'):
            hrp, data = bech32_decode(address)
            if hrp not in ('bc', 'tb') or data is None:
                return False
            return 6 <= len(data) <= 40
        
        # Checking Base58 (Legacy)
        if not re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return False
        
        # Base58Check checksum verification
        try:
            decoded = bytes.fromhex(base58_decode(address))
            checksum = decoded[-4:]
            hash256 = sha256(sha256(decoded[:-4]).digest()).digest()
            return checksum == hash256[:4]
        except:
            return False

    @staticmethod
    def _validate_eth(address: str) -> bool:
        """Ethereum: EIP-55 checksum validation"""
        # Basic format
        if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
            return False
        
        # EIP-55 checksum
        address = address[2:]
        address_hash = sha3_256(address.lower().encode()).hexdigest()
        
        for i in range(40):
            if (int(address_hash[i], 16) >= 8 and
                address[i].upper() != address[i]):
                return False
            elif (int(address_hash[i], 16) < 8 and
                address[i].lower() != address[i]):
                return False
        return True

    @staticmethod
    def _validate_ltc(address: str) -> bool:
        """Litecoin: legacy, P2SH и Bech32"""
        # Legacy (L...)
        if re.match(r'^[LM][a-km-zA-HJ-NP-Z1-9]{26,33}$', address):
            return True
        
        # P2SH (M... or 3...)
        if re.match(r'^[M3][a-km-zA-HJ-NP-Z1-9]{26,33}$', address):
            return True
        
        # Bech32 (ltc1...)
        if address.startswith('ltc1'):
            hrp, data = bech32_decode(address)
            if hrp != 'ltc' or data is None:
                return False
            return 6 <= len(data) <= 40
        
        return False

    @staticmethod
    def _validate_bnb(address: str) -> bool:
        """Binance Chain: bnb1... и Ethereum-style"""
        # BNB Bech32
        if address.startswith('bnb1'):
            hrp, data = bech32_decode(address)
            if hrp != 'bnb' or data is None:
                return False
            return len(data) == 32
        
        # Ethereum-style проверка
        return CryptoValidator._validate_eth(address)

    @staticmethod
    def base58_decode(address: str) -> str:
        """Base58 decoding with checksum verification"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        decoded = 0
        for char in address:
            decoded = decoded * 58 + alphabet.index(char)
        return hex(decoded)[2:-8]
