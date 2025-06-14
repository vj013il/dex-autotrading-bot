import asyncio
import platform
from web3 import Web3

class TokenHandler:
    def __init__(self, web3_provider="https://mainnet.infura.io/v3/YOUR_INFURA_KEY"):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.token_address = None
        self.erc20_abi = [
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
        ]

    async def validate_token(self, token_address):
        if not self.w3.isChecksumAddress(token_address):
            return False
        try:
            token_contract = self.w3.eth.contract(address=token_address, abi=self.erc20_abi)
            await asyncio.sleep(0.1)  # Имитация задержки для Pyodide
            token_name = token_contract.functions.name().call()
            return bool(token_name)
        except Exception:
            return False

    async def set_token(self, token_address):
        if await self.validate_token(token_address):
            self.token_address = token_address
            return {"status": "success", "message": f"Token {token_address} validated"}
        return {"status": "error", "message": "Invalid token address"}

if platform.system() == "Emscripten":
    asyncio.ensure_future(TokenHandler().validate_token("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"))
