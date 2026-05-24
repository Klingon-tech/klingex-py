"""Mining pool endpoints - public stats + authenticated miner data.

Public endpoints (no auth):
- :meth:`get_configs` - list of enabled algorithm/coin configurations
- :meth:`get_blocks` - recently found blocks
- :meth:`get_stats` - per-symbol pool & network hashrate snapshot/history
- :meth:`get_leaderboard` - top miners for a symbol/period

Authenticated endpoints (API key ``read`` scope):
- :meth:`get_my_workers` - the caller's connected stratum workers
- :meth:`get_my_rewards` - the caller's PPLNS rewards
- :meth:`get_my_payouts` - the caller's credited payouts
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import (
    MiningPoolConfig,
    MiningBlock,
    MiningBlocksResponse,
    MiningStats,
    MiningLeaderboard,
    MiningWorkersResponse,
    MiningRewardsResponse,
    MiningPayoutsResponse,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


def _list_params(
    limit: Optional[int],
    offset: Optional[int],
    symbol: Optional[str],
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if symbol is not None:
        params["symbol"] = symbol
    return params


class MiningPoolEndpoint:
    """Mining pool endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    # ---- public ----
    def get_configs(self) -> List[MiningPoolConfig]:
        """List enabled mining-pool configurations (algorithm, port, fee, hashrate)."""
        data = self._client.get("/api/pool/configs")
        pools = data.get("pools", data) if isinstance(data, dict) else data
        return [MiningPoolConfig.model_validate(p) for p in (pools or [])]

    def get_blocks(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningBlocksResponse:
        """List recent blocks found by the pool."""
        data = self._client.get(
            "/api/pool/blocks", params=_list_params(limit, offset, symbol) or None
        )
        return MiningBlocksResponse.model_validate(data)

    def get_stats(self, symbol: str, period: str = "24h") -> MiningStats:
        """Pool & network hashrate snapshot + history for a coin.

        Args:
            symbol: Coin ticker (e.g. ``"XMR"``).
            period: ``1h``, ``6h``, ``24h``, ``7d`` or ``30d``.
        """
        data = self._client.get(
            "/api/pool/stats", params={"symbol": symbol, "period": period}
        )
        return MiningStats.model_validate(data)

    def get_leaderboard(self, symbol: str, period: str = "24h") -> MiningLeaderboard:
        """Top miners for a coin and time window."""
        data = self._client.get(
            "/api/pool/leaderboard", params={"symbol": symbol, "period": period}
        )
        return MiningLeaderboard.model_validate(data)

    # ---- authenticated ----
    def get_my_workers(self, symbol: Optional[str] = None) -> MiningWorkersResponse:
        """List the authenticated user's connected workers."""
        params = {"symbol": symbol} if symbol else None
        data = self._client.get(
            "/api/pool/my-workers", params=params, authenticated=True
        )
        return MiningWorkersResponse.model_validate(data)

    def get_my_rewards(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningRewardsResponse:
        """List the authenticated user's PPLNS rewards."""
        data = self._client.get(
            "/api/pool/my-rewards",
            params=_list_params(limit, offset, symbol) or None,
            authenticated=True,
        )
        return MiningRewardsResponse.model_validate(data)

    def get_my_payouts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningPayoutsResponse:
        """List the authenticated user's credited payouts."""
        data = self._client.get(
            "/api/pool/my-payouts",
            params=_list_params(limit, offset, symbol) or None,
            authenticated=True,
        )
        return MiningPayoutsResponse.model_validate(data)


class AsyncMiningPoolEndpoint:
    """Mining pool endpoints (async)."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_configs(self) -> List[MiningPoolConfig]:
        data = await self._client.get("/api/pool/configs")
        pools = data.get("pools", data) if isinstance(data, dict) else data
        return [MiningPoolConfig.model_validate(p) for p in (pools or [])]

    async def get_blocks(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningBlocksResponse:
        data = await self._client.get(
            "/api/pool/blocks", params=_list_params(limit, offset, symbol) or None
        )
        return MiningBlocksResponse.model_validate(data)

    async def get_stats(self, symbol: str, period: str = "24h") -> MiningStats:
        data = await self._client.get(
            "/api/pool/stats", params={"symbol": symbol, "period": period}
        )
        return MiningStats.model_validate(data)

    async def get_leaderboard(self, symbol: str, period: str = "24h") -> MiningLeaderboard:
        data = await self._client.get(
            "/api/pool/leaderboard", params={"symbol": symbol, "period": period}
        )
        return MiningLeaderboard.model_validate(data)

    async def get_my_workers(self, symbol: Optional[str] = None) -> MiningWorkersResponse:
        params = {"symbol": symbol} if symbol else None
        data = await self._client.get(
            "/api/pool/my-workers", params=params, authenticated=True
        )
        return MiningWorkersResponse.model_validate(data)

    async def get_my_rewards(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningRewardsResponse:
        data = await self._client.get(
            "/api/pool/my-rewards",
            params=_list_params(limit, offset, symbol) or None,
            authenticated=True,
        )
        return MiningRewardsResponse.model_validate(data)

    async def get_my_payouts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> MiningPayoutsResponse:
        data = await self._client.get(
            "/api/pool/my-payouts",
            params=_list_params(limit, offset, symbol) or None,
            authenticated=True,
        )
        return MiningPayoutsResponse.model_validate(data)
