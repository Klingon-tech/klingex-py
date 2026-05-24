"""Gift codes endpoint - create redeemable crypto voucher codes.

Only the creation endpoints accept API keys (``trade`` scope). Redeem,
preview, my-codes, etc. are JWT-only and not exposed in the SDK.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

from klingex.types import (
    GiftCodeResponse,
    BulkGiftCodeResponse,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


def _create_payload(
    asset_id: int,
    amount: str,
    message: Optional[str],
    hide_amount: bool,
    expires_in_days: Optional[int],
    two_factor_code: Optional[str],
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "asset_id": asset_id,
        "amount": amount,
        "hide_amount": hide_amount,
    }
    if message:
        data["message"] = message
    if expires_in_days is not None:
        data["expires_in_days"] = expires_in_days
    if two_factor_code:
        data["two_factor_code"] = two_factor_code
    return data


def _bulk_payload(
    asset_id: int,
    amount_per_code: str,
    count: int,
    message: Optional[str],
    hide_amount: bool,
    expires_in_days: Optional[int],
    two_factor_code: Optional[str],
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "asset_id": asset_id,
        "amount_per_code": amount_per_code,
        "count": count,
        "hide_amount": hide_amount,
    }
    if message:
        data["message"] = message
    if expires_in_days is not None:
        data["expires_in_days"] = expires_in_days
    if two_factor_code:
        data["two_factor_code"] = two_factor_code
    return data


class GiftCodesEndpoint:
    """Gift code endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def create(
        self,
        asset_id: int,
        amount: str,
        message: Optional[str] = None,
        hide_amount: bool = False,
        expires_in_days: Optional[int] = None,
        two_factor_code: Optional[str] = None,
    ) -> GiftCodeResponse:
        """Create a single gift code.

        Args:
            asset_id: Numeric asset ID for the deposit.
            amount: **Raw integer base units** as a string (e.g. for BTC
                this is satoshis: ``"10000000"`` = 0.1 BTC). Decimal
                points and scientific notation are rejected — convert
                from human-readable using the asset's ``decimals`` first.
            message: Optional message attached to the code (max 500 chars).
            hide_amount: If ``True`` the redeemer sees no amount until
                they redeem.
            expires_in_days: 1-365. ``None`` uses the system default.
            two_factor_code: 6-digit TOTP, when required by the account.

        Requires the ``trade`` scope on the API key.
        """
        response = self._client.post(
            "/api/gift-codes",
            data=_create_payload(
                asset_id, amount, message, hide_amount, expires_in_days, two_factor_code
            ),
            authenticated=True,
        )
        return GiftCodeResponse.model_validate(response)

    def create_bulk(
        self,
        asset_id: int,
        amount_per_code: str,
        count: int,
        message: Optional[str] = None,
        hide_amount: bool = False,
        expires_in_days: Optional[int] = None,
        two_factor_code: Optional[str] = None,
    ) -> BulkGiftCodeResponse:
        """Create many gift codes at once.

        Args:
            amount_per_code: **Raw integer base units** per code (same
                rules as :meth:`create`'s ``amount``).
            count: 2-100.
        """
        response = self._client.post(
            "/api/gift-codes/bulk",
            data=_bulk_payload(
                asset_id, amount_per_code, count, message, hide_amount,
                expires_in_days, two_factor_code,
            ),
            authenticated=True,
        )
        return BulkGiftCodeResponse.model_validate(response)


class AsyncGiftCodesEndpoint:
    """Gift code endpoints (async)."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def create(
        self,
        asset_id: int,
        amount: str,
        message: Optional[str] = None,
        hide_amount: bool = False,
        expires_in_days: Optional[int] = None,
        two_factor_code: Optional[str] = None,
    ) -> GiftCodeResponse:
        response = await self._client.post(
            "/api/gift-codes",
            data=_create_payload(
                asset_id, amount, message, hide_amount, expires_in_days, two_factor_code
            ),
            authenticated=True,
        )
        return GiftCodeResponse.model_validate(response)

    async def create_bulk(
        self,
        asset_id: int,
        amount_per_code: str,
        count: int,
        message: Optional[str] = None,
        hide_amount: bool = False,
        expires_in_days: Optional[int] = None,
        two_factor_code: Optional[str] = None,
    ) -> BulkGiftCodeResponse:
        response = await self._client.post(
            "/api/gift-codes/bulk",
            data=_bulk_payload(
                asset_id, amount_per_code, count, message, hide_amount,
                expires_in_days, two_factor_code,
            ),
            authenticated=True,
        )
        return BulkGiftCodeResponse.model_validate(response)
