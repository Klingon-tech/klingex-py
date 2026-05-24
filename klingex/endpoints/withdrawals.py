"""Withdrawals endpoint - submit on-chain withdrawals via API key.

Only the submission endpoint accepts API keys (with the ``withdraw`` scope).
The validate-address, history, 2FA, and email-confirmation routes are
JWT-only and intentionally not exposed in the SDK.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

from klingex.types import WithdrawalSubmitResponse

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


def _build_payload(
    symbol: str,
    asset_id: int,
    amount: str,
    address: str,
    destination_tag: Optional[int],
    memo: Optional[str],
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "symbol": symbol,
        "assetId": asset_id,
        "amount": amount,
        "address": address,
    }
    if destination_tag is not None:
        data["destinationTag"] = destination_tag
    if memo:
        data["memo"] = memo
    return data


class WithdrawalsEndpoint:
    """Withdrawal endpoints accessible via API keys with the ``withdraw`` scope."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def submit(
        self,
        symbol: str,
        asset_id: int,
        amount: str,
        address: str,
        destination_tag: Optional[int] = None,
        memo: Optional[str] = None,
    ) -> WithdrawalSubmitResponse:
        """Submit an on-chain withdrawal.

        API keys with the ``withdraw`` scope skip interactive 2FA and
        email confirmation; the 2FA gate was enforced when the scope
        was granted.

        Args:
            symbol: Asset symbol (e.g. ``"BTC"``, ``"ETH"``).
            asset_id: Numeric asset ID.
            amount: **Raw integer base units** as a string (e.g. for BTC
                this is satoshis: ``"10000000"`` = 0.1 BTC). Decimal
                points and scientific notation are rejected — convert
                from human-readable using the asset's ``decimals`` first.
            address: Destination address.
            destination_tag: XRP-style uint32 destination tag.
            memo: Free-form string memo for Graphene chains (BLURT, etc.).

        Returns:
            :class:`WithdrawalSubmitResponse` with ``message`` and
            ``withdrawal_id``.
        """
        response = self._client.post(
            "/api/submit-withdraw",
            data=_build_payload(symbol, asset_id, amount, address, destination_tag, memo),
            authenticated=True,
        )
        return WithdrawalSubmitResponse.model_validate(response)


class AsyncWithdrawalsEndpoint:
    """Async variant of :class:`WithdrawalsEndpoint`."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def submit(
        self,
        symbol: str,
        asset_id: int,
        amount: str,
        address: str,
        destination_tag: Optional[int] = None,
        memo: Optional[str] = None,
    ) -> WithdrawalSubmitResponse:
        response = await self._client.post(
            "/api/submit-withdraw",
            data=_build_payload(symbol, asset_id, amount, address, destination_tag, memo),
            authenticated=True,
        )
        return WithdrawalSubmitResponse.model_validate(response)
