"""Markets endpoint - public market data."""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

from klingex.types import (
    Asset,
    AssetInfo,
    Market,
    Ticker,
    OrderBook,
    OHLCV,
    MarketInfo,
    MarketSparklinesResponse,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class MarketsEndpoint:
    """Public market data endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def get_assets(self) -> List[Asset]:
        """List all available assets."""
        data = self._client.get("/api/assets")
        assets_data = data.get("assets", data) if isinstance(data, dict) else data
        return [Asset.model_validate(a) for a in assets_data]

    def get_markets(self) -> List[Market]:
        """List all available markets."""
        data = self._client.get("/api/markets")
        return [Market.model_validate(m) for m in data]

    def get_market(self, market_id: int) -> Market:
        """Return a single market by ID."""
        for m in self.get_markets():
            if m.id == market_id:
                return m
        raise ValueError(f"Market {market_id} not found")

    def get_tickers(self) -> List[Ticker]:
        """Return tickers for all markets (CMC/CoinGecko shape)."""
        data = self._client.get("/api/tickers")
        return [Ticker.model_validate(t) for t in data]

    def get_ticker(self, ticker_id: str) -> Ticker:
        """Return a single ticker by ticker id (e.g. ``BTC_USDT``)."""
        for t in self.get_tickers():
            if t.ticker_id == ticker_id:
                return t
        raise ValueError(f"Ticker {ticker_id} not found")

    def get_orderbook(self, market_id: int) -> OrderBook:
        """Fetch the orderbook snapshot for a market."""
        data = self._client.get(
            "/api/orderbook", params={"marketId": market_id, "isCmc": "false"}
        )
        return OrderBook.model_validate(data)

    def get_ohlcv(
        self,
        market_id: int,
        timeframe: str = "5m",
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[OHLCV]:
        """Fetch OHLCV candles for a market.

        Args:
            market_id: Trading pair ID.
            timeframe: One of ``1m, 5m, 15m, 30m, 1h, 4h, 1D``.
            limit: Max candles to return.
            start_date: ISO-8601 start time (RFC3339).
            end_date: ISO-8601 end time (RFC3339).
        """
        params: Dict[str, Any] = {"marketId": market_id, "timeframe": timeframe}
        if limit:
            params["limit"] = limit
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._client.get("/api/ohlcv", params=params)
        return [OHLCV.model_validate(o) for o in data]

    def get_sparklines(
        self,
        timeframe: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> MarketSparklinesResponse:
        """Return sparkline data for every market.

        Args:
            timeframe: Sparkline bucket (e.g. ``1h``).
            limit: Number of points per market.
        """
        params: Dict[str, Any] = {}
        if timeframe:
            params["timeframe"] = timeframe
        if limit:
            params["limit"] = limit
        data = self._client.get("/api/markets/sparklines", params=params or None)
        return MarketSparklinesResponse.model_validate(data)

    def get_market_info(self, base_symbol: str, quote_symbol: str) -> MarketInfo:
        """Return the market-info row for a base/quote pair."""
        data = self._client.get(
            "/api/market-info",
            params={"baseAssetSymbol": base_symbol, "quoteAssetSymbol": quote_symbol},
        )
        return MarketInfo.model_validate(data)

    def get_asset_info(self, asset: Union[int, str]) -> AssetInfo:
        """Return detailed asset info by ID or symbol."""
        if isinstance(asset, int):
            data = self._client.get(f"/api/asset-info/{asset}")
        else:
            data = self._client.get(f"/api/asset-info/symbol/{asset}")
        return AssetInfo.model_validate(data)


class AsyncMarketsEndpoint:
    """Public market data endpoints (async)."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_assets(self) -> List[Asset]:
        data = await self._client.get("/api/assets")
        assets_data = data.get("assets", data) if isinstance(data, dict) else data
        return [Asset.model_validate(a) for a in assets_data]

    async def get_markets(self) -> List[Market]:
        data = await self._client.get("/api/markets")
        return [Market.model_validate(m) for m in data]

    async def get_market(self, market_id: int) -> Market:
        for m in await self.get_markets():
            if m.id == market_id:
                return m
        raise ValueError(f"Market {market_id} not found")

    async def get_tickers(self) -> List[Ticker]:
        data = await self._client.get("/api/tickers")
        return [Ticker.model_validate(t) for t in data]

    async def get_ticker(self, ticker_id: str) -> Ticker:
        for t in await self.get_tickers():
            if t.ticker_id == ticker_id:
                return t
        raise ValueError(f"Ticker {ticker_id} not found")

    async def get_orderbook(self, market_id: int) -> OrderBook:
        data = await self._client.get(
            "/api/orderbook", params={"marketId": market_id, "isCmc": "false"}
        )
        return OrderBook.model_validate(data)

    async def get_ohlcv(
        self,
        market_id: int,
        timeframe: str = "5m",
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[OHLCV]:
        params: Dict[str, Any] = {"marketId": market_id, "timeframe": timeframe}
        if limit:
            params["limit"] = limit
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = await self._client.get("/api/ohlcv", params=params)
        return [OHLCV.model_validate(o) for o in data]

    async def get_sparklines(
        self,
        timeframe: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> MarketSparklinesResponse:
        params: Dict[str, Any] = {}
        if timeframe:
            params["timeframe"] = timeframe
        if limit:
            params["limit"] = limit
        data = await self._client.get("/api/markets/sparklines", params=params or None)
        return MarketSparklinesResponse.model_validate(data)

    async def get_market_info(self, base_symbol: str, quote_symbol: str) -> MarketInfo:
        data = await self._client.get(
            "/api/market-info",
            params={"baseAssetSymbol": base_symbol, "quoteAssetSymbol": quote_symbol},
        )
        return MarketInfo.model_validate(data)

    async def get_asset_info(self, asset: Union[int, str]) -> AssetInfo:
        if isinstance(asset, int):
            data = await self._client.get(f"/api/asset-info/{asset}")
        else:
            data = await self._client.get(f"/api/asset-info/symbol/{asset}")
        return AssetInfo.model_validate(data)
