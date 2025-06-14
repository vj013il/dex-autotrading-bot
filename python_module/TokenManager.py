import asyncio
import platform
from PyQt5.QtWidgets import QMessageBox

class TokenManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.token_address = ""

    async def validate_token(self, address):
        if not address.startswith('0x') or len(address) != 42:
            return False
        await asyncio.sleep(0.1)  # Имитация задержки
        return True

    def set_token(self, address):
        asyncio.ensure_future(self._set_token_async(address))

    async def _set_token_async(self, address):
        if await self.validate_token(address):
            self.token_address = address
            self.parent.send_request('/api/set_token', {'token_address': address})
            QMessageBox.information(self.parent, "Success", "Token set successfully")
        else:
            QMessageBox.warning(self.parent, "Error", "Invalid token address")

if platform.system() == "Emscripten":
    asyncio.ensure_future(TokenManager().validate_token("0x123"))  # Пример для Pyodide
