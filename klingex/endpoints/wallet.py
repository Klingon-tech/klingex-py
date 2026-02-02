"""
Wallet Endpoint - Balance management
"""

from typing import List, TYPE_CHECKING

from klingex.types import Balance

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class WalletEndpoint:
    """Wallet management endpoints"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def get_balances(self) -> List[Balance]:
        """Get all wallet balances"""
        data = self._client.get("/api/user-balances", authenticated=True)
        return [Balance.model_validate(b) for b in data]

    def get_balance(self, symbol: str) -> Balance:
        """Get balance for a specific asset

        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH")
        """
        balances = self.get_balances()
        for balance in balances:
            if balance.symbol == symbol:
                return balance
        raise ValueError(f"Balance for {symbol} not found")


class AsyncWalletEndpoint:
    """Async wallet management endpoints"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_balances(self) -> List[Balance]:
        """Get all wallet balances"""
        data = await self._client.get("/api/user-balances", authenticated=True)
        return [Balance.model_validate(b) for b in data]

    async def get_balance(self, symbol: str) -> Balance:
        """Get balance for a specific asset"""
        balances = await self.get_balances()
        for balance in balances:
            if balance.symbol == symbol:
                return balance
        raise ValueError(f"Balance for {symbol} not found")
