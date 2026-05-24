"""Liquidity pool endpoints - AMM pool data and LP operations.

- ``list`` and ``get`` are public (no auth).
- ``positions`` / ``position_history`` require an API key with the ``read`` scope.
- ``add_liquidity`` / ``remove_liquidity`` require an API key with the ``liquidity`` scope.
"""

from typing import Any, Dict, List, TYPE_CHECKING

from klingex.http import KlingExError
from klingex.types import (
    Pool,
    PoolDetail,
    LPPosition,
    PositionHistoryResponse,
    AddLiquidityResult,
    RemoveLiquidityResult,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


def _unwrap(response: Any) -> Any:
    """Pool routes wrap their payload in ``{"success": true, "data": ...}``."""
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response


def _add_payload(pool_id: int, base_amount_max: str, quote_amount_max: str, min_lp_tokens: str) -> Dict[str, Any]:
    return {
        "pool_id": pool_id,
        "base_amount_max": base_amount_max,
        "quote_amount_max": quote_amount_max,
        "min_lp_tokens": min_lp_tokens,
    }


def _remove_payload(pool_id: int, lp_tokens: str, min_base_out: str, min_quote_out: str) -> Dict[str, Any]:
    return {
        "pool_id": pool_id,
        "lp_tokens": lp_tokens,
        "min_base_out": min_base_out,
        "min_quote_out": min_quote_out,
    }


def _empty_history(pool_id: int) -> PositionHistoryResponse:
    return PositionHistoryResponse(
        pool_id=pool_id,
        base_symbol="",
        quote_symbol="",
        base_decimals=0,
        quote_decimals=0,
        history=[],
    )


class PoolsEndpoint:
    """Liquidity pool endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self) -> List[Pool]:
        """List every active, public liquidity pool (no auth)."""
        data = _unwrap(self._client.get("/api/pools/list"))
        return [Pool.model_validate(p) for p in (data or [])]

    def get(self, pool_id: int) -> PoolDetail:
        """Fetch a single pool by ID (no auth)."""
        data = _unwrap(self._client.get(f"/api/pools/{pool_id}"))
        return PoolDetail.model_validate(data)

    def positions(self) -> List[LPPosition]:
        """Return the authenticated user's LP positions across all pools."""
        data = _unwrap(self._client.get("/api/pools/positions", authenticated=True))
        return [LPPosition.model_validate(p) for p in (data or [])]

    def position_history(self, pool_id: int, days: int = 30) -> PositionHistoryResponse:
        """Historical chart data for the user's position in one pool.

        Returns an empty history response if the user has no recorded
        snapshots for the pool (the backend currently returns 404 for
        that case).
        """
        try:
            data = _unwrap(self._client.get(
                "/api/pools/positions/history",
                params={"pool_id": pool_id, "days": days},
                authenticated=True,
            ))
        except KlingExError as exc:
            if exc.status_code == 404:
                return _empty_history(pool_id)
            raise
        return PositionHistoryResponse.model_validate(data)

    def add_liquidity(
        self,
        pool_id: int,
        base_amount_max: str,
        quote_amount_max: str,
        min_lp_tokens: str,
    ) -> AddLiquidityResult:
        """Deposit liquidity into a pool. Requires ``liquidity`` scope."""
        data = _unwrap(self._client.post(
            "/api/pools/add-liquidity",
            data=_add_payload(pool_id, base_amount_max, quote_amount_max, min_lp_tokens),
            authenticated=True,
        ))
        return AddLiquidityResult.model_validate(data)

    def remove_liquidity(
        self,
        pool_id: int,
        lp_tokens: str,
        min_base_out: str,
        min_quote_out: str,
    ) -> RemoveLiquidityResult:
        """Burn LP tokens and withdraw the underlying assets."""
        data = _unwrap(self._client.post(
            "/api/pools/remove-liquidity",
            data=_remove_payload(pool_id, lp_tokens, min_base_out, min_quote_out),
            authenticated=True,
        ))
        return RemoveLiquidityResult.model_validate(data)


class AsyncPoolsEndpoint:
    """Async variant of :class:`PoolsEndpoint`."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def list(self) -> List[Pool]:
        data = _unwrap(await self._client.get("/api/pools/list"))
        return [Pool.model_validate(p) for p in (data or [])]

    async def get(self, pool_id: int) -> PoolDetail:
        data = _unwrap(await self._client.get(f"/api/pools/{pool_id}"))
        return PoolDetail.model_validate(data)

    async def positions(self) -> List[LPPosition]:
        data = _unwrap(await self._client.get("/api/pools/positions", authenticated=True))
        return [LPPosition.model_validate(p) for p in (data or [])]

    async def position_history(self, pool_id: int, days: int = 30) -> PositionHistoryResponse:
        try:
            data = _unwrap(await self._client.get(
                "/api/pools/positions/history",
                params={"pool_id": pool_id, "days": days},
                authenticated=True,
            ))
        except KlingExError as exc:
            if exc.status_code == 404:
                return _empty_history(pool_id)
            raise
        return PositionHistoryResponse.model_validate(data)

    async def add_liquidity(
        self,
        pool_id: int,
        base_amount_max: str,
        quote_amount_max: str,
        min_lp_tokens: str,
    ) -> AddLiquidityResult:
        data = _unwrap(await self._client.post(
            "/api/pools/add-liquidity",
            data=_add_payload(pool_id, base_amount_max, quote_amount_max, min_lp_tokens),
            authenticated=True,
        ))
        return AddLiquidityResult.model_validate(data)

    async def remove_liquidity(
        self,
        pool_id: int,
        lp_tokens: str,
        min_base_out: str,
        min_quote_out: str,
    ) -> RemoveLiquidityResult:
        data = _unwrap(await self._client.post(
            "/api/pools/remove-liquidity",
            data=_remove_payload(pool_id, lp_tokens, min_base_out, min_quote_out),
            authenticated=True,
        ))
        return RemoveLiquidityResult.model_validate(data)
