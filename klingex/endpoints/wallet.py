"""
Wallet Endpoint - Balance and deposit/withdrawal management
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Balance, Deposit, Withdrawal, DepositAddress

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class WalletEndpoint:
    """Wallet management endpoints (authenticated)"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def get_balances(self) -> List[Balance]:
        """Get all wallet balances"""
        data = self._client.get("/api/wallet/balances", authenticated=True)
        balances_data = data.get("balances", data) if isinstance(data, dict) else data
        return [Balance.model_validate(b) for b in balances_data]

    def get_balance(self, asset_id: str) -> Balance:
        """Get balance for a specific asset

        Args:
            asset_id: Asset identifier
        """
        data = self._client.get(f"/api/wallet/balances/{asset_id}", authenticated=True)
        return Balance.model_validate(data)

    def get_deposit_address(self, asset_id: str, chain: Optional[str] = None) -> DepositAddress:
        """Get deposit address for an asset

        Args:
            asset_id: Asset identifier
            chain: Optional chain for multi-chain assets (e.g., "erc20", "bep20")
        """
        params = {"chain": chain} if chain else None
        data = self._client.get(
            f"/api/wallet/deposit-address/{asset_id}",
            params=params,
            authenticated=True,
        )
        return DepositAddress.model_validate(data)

    def get_deposits(
        self,
        asset_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Deposit]:
        """Get deposit history

        Args:
            asset_id: Optional asset ID to filter by
            status: Optional status to filter by (pending, confirmed, failed)
            limit: Maximum number of deposits to return
            offset: Pagination offset
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if asset_id:
            params["assetId"] = asset_id
        if status:
            params["status"] = status

        data = self._client.get("/api/wallet/deposits", params=params, authenticated=True)
        deposits_data = data.get("deposits", data) if isinstance(data, dict) else data
        return [Deposit.model_validate(d) for d in deposits_data]

    def get_deposit(self, deposit_id: str) -> Deposit:
        """Get a specific deposit by ID

        Args:
            deposit_id: Deposit ID
        """
        data = self._client.get(f"/api/wallet/deposits/{deposit_id}", authenticated=True)
        return Deposit.model_validate(data)

    def request_withdrawal(
        self,
        asset_id: str,
        amount: str,
        address: str,
        memo: Optional[str] = None,
        two_fa_code: Optional[str] = None,
    ) -> Withdrawal:
        """Request a withdrawal

        Args:
            asset_id: Asset identifier
            amount: Withdrawal amount (human-readable)
            address: Destination address
            memo: Optional memo/tag for chains that require it
            two_fa_code: 2FA code if enabled on account
        """
        data: Dict[str, Any] = {
            "assetId": asset_id,
            "amount": amount,
            "address": address,
        }
        if memo:
            data["memo"] = memo
        if two_fa_code:
            data["twoFaCode"] = two_fa_code

        result = self._client.post("/api/wallet/withdraw", data=data, authenticated=True)
        return Withdrawal.model_validate(result)

    def get_withdrawals(
        self,
        asset_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Withdrawal]:
        """Get withdrawal history

        Args:
            asset_id: Optional asset ID to filter by
            status: Optional status to filter by (pending, processing, completed, failed)
            limit: Maximum number of withdrawals to return
            offset: Pagination offset
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if asset_id:
            params["assetId"] = asset_id
        if status:
            params["status"] = status

        data = self._client.get("/api/wallet/withdrawals", params=params, authenticated=True)
        withdrawals_data = data.get("withdrawals", data) if isinstance(data, dict) else data
        return [Withdrawal.model_validate(w) for w in withdrawals_data]

    def get_withdrawal(self, withdrawal_id: str) -> Withdrawal:
        """Get a specific withdrawal by ID

        Args:
            withdrawal_id: Withdrawal ID
        """
        data = self._client.get(f"/api/wallet/withdrawals/{withdrawal_id}", authenticated=True)
        return Withdrawal.model_validate(data)


class AsyncWalletEndpoint:
    """Async wallet management endpoints (authenticated)"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_balances(self) -> List[Balance]:
        """Get all wallet balances"""
        data = await self._client.get("/api/wallet/balances", authenticated=True)
        balances_data = data.get("balances", data) if isinstance(data, dict) else data
        return [Balance.model_validate(b) for b in balances_data]

    async def get_balance(self, asset_id: str) -> Balance:
        """Get balance for a specific asset"""
        data = await self._client.get(f"/api/wallet/balances/{asset_id}", authenticated=True)
        return Balance.model_validate(data)

    async def get_deposit_address(
        self, asset_id: str, chain: Optional[str] = None
    ) -> DepositAddress:
        """Get deposit address for an asset"""
        params = {"chain": chain} if chain else None
        data = await self._client.get(
            f"/api/wallet/deposit-address/{asset_id}",
            params=params,
            authenticated=True,
        )
        return DepositAddress.model_validate(data)

    async def get_deposits(
        self,
        asset_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Deposit]:
        """Get deposit history"""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if asset_id:
            params["assetId"] = asset_id
        if status:
            params["status"] = status

        data = await self._client.get("/api/wallet/deposits", params=params, authenticated=True)
        deposits_data = data.get("deposits", data) if isinstance(data, dict) else data
        return [Deposit.model_validate(d) for d in deposits_data]

    async def get_deposit(self, deposit_id: str) -> Deposit:
        """Get a specific deposit by ID"""
        data = await self._client.get(f"/api/wallet/deposits/{deposit_id}", authenticated=True)
        return Deposit.model_validate(data)

    async def request_withdrawal(
        self,
        asset_id: str,
        amount: str,
        address: str,
        memo: Optional[str] = None,
        two_fa_code: Optional[str] = None,
    ) -> Withdrawal:
        """Request a withdrawal"""
        data: Dict[str, Any] = {
            "assetId": asset_id,
            "amount": amount,
            "address": address,
        }
        if memo:
            data["memo"] = memo
        if two_fa_code:
            data["twoFaCode"] = two_fa_code

        result = await self._client.post("/api/wallet/withdraw", data=data, authenticated=True)
        return Withdrawal.model_validate(result)

    async def get_withdrawals(
        self,
        asset_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Withdrawal]:
        """Get withdrawal history"""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if asset_id:
            params["assetId"] = asset_id
        if status:
            params["status"] = status

        data = await self._client.get("/api/wallet/withdrawals", params=params, authenticated=True)
        withdrawals_data = data.get("withdrawals", data) if isinstance(data, dict) else data
        return [Withdrawal.model_validate(w) for w in withdrawals_data]

    async def get_withdrawal(self, withdrawal_id: str) -> Withdrawal:
        """Get a specific withdrawal by ID"""
        data = await self._client.get(
            f"/api/wallet/withdrawals/{withdrawal_id}", authenticated=True
        )
        return Withdrawal.model_validate(data)
