"""Wallet endpoint - user balances and public wallet system status."""

from typing import List, TYPE_CHECKING

from klingex.types import (
    Balance,
    WalletSystemStatus,
    AssetSyncStatus,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class WalletEndpoint:
    """Wallet management endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def get_balances(self) -> List[Balance]:
        """Return every wallet balance for the authenticated user."""
        data = self._client.get("/api/user-balances", authenticated=True)
        return [Balance.model_validate(b) for b in data]

    def get_balance(self, symbol: str) -> Balance:
        """Return the balance for a single asset (by symbol)."""
        for b in self.get_balances():
            if b.symbol == symbol:
                return b
        raise ValueError(f"Balance for {symbol} not found")

    # Public wallet system status (no auth)
    def get_wallets_status(self) -> WalletSystemStatus:
        """Fetch the public wallet-system health snapshot.

        Returns information about each on-chain asset's sync state -
        block number, last-processed timestamp, and overall status.
        """
        data = self._client.get("/api/wallets/status")
        return WalletSystemStatus.model_validate(data)

    def get_wallet_status(self, asset_id: int) -> AssetSyncStatus:
        """Fetch the sync status for a single asset by ID."""
        data = self._client.get(f"/api/wallets/status/{asset_id}")
        return AssetSyncStatus.model_validate(data)


class AsyncWalletEndpoint:
    """Wallet management endpoints (async)."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_balances(self) -> List[Balance]:
        data = await self._client.get("/api/user-balances", authenticated=True)
        return [Balance.model_validate(b) for b in data]

    async def get_balance(self, symbol: str) -> Balance:
        for b in await self.get_balances():
            if b.symbol == symbol:
                return b
        raise ValueError(f"Balance for {symbol} not found")

    async def get_wallets_status(self) -> WalletSystemStatus:
        data = await self._client.get("/api/wallets/status")
        return WalletSystemStatus.model_validate(data)

    async def get_wallet_status(self, asset_id: int) -> AssetSyncStatus:
        data = await self._client.get(f"/api/wallets/status/{asset_id}")
        return AssetSyncStatus.model_validate(data)
