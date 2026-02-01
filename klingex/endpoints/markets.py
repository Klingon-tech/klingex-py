"""
Markets Endpoint - Public market data
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Asset, Market, Ticker, OrderBook, OrderBookEntry, OHLCV, Trade

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class MarketsEndpoint:
    """Public market data endpoints"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def get_assets(self) -> List[Asset]:
        """Get all available assets"""
        data = self._client.get("/api/assets")
        assets_data = data.get("assets", data) if isinstance(data, dict) else data
        return [Asset.model_validate(a) for a in assets_data]

    def get_asset(self, asset_id: str) -> Asset:
        """Get a specific asset by ID"""
        data = self._client.get(f"/api/assets/{asset_id}")
        return Asset.model_validate(data)

    def get_markets(self) -> List[Market]:
        """Get all available markets"""
        data = self._client.get("/api/markets")
        markets_data = data.get("markets", data) if isinstance(data, dict) else data
        return [Market.model_validate(m) for m in markets_data]

    def get_market(self, market_id: str) -> Market:
        """Get a specific market by ID"""
        data = self._client.get(f"/api/markets/{market_id}")
        return Market.model_validate(data)

    def get_tickers(self) -> List[Ticker]:
        """Get tickers for all markets"""
        data = self._client.get("/api/tickers")
        tickers_data = data.get("tickers", data) if isinstance(data, dict) else data
        return [Ticker.model_validate(t) for t in tickers_data]

    def get_ticker(self, market_id: str) -> Ticker:
        """Get ticker for a specific market"""
        data = self._client.get(f"/api/tickers/{market_id}")
        return Ticker.model_validate(data)

    def get_orderbook(self, market_id: str, depth: int = 50) -> OrderBook:
        """Get orderbook for a market

        Args:
            market_id: Market identifier
            depth: Number of levels to return (default: 50)
        """
        data = self._client.get(f"/api/orderbook/{market_id}", params={"depth": depth})
        return OrderBook.model_validate(data)

    def get_trades(
        self,
        market_id: str,
        limit: int = 100,
        before: Optional[str] = None,
    ) -> List[Trade]:
        """Get recent trades for a market

        Args:
            market_id: Market identifier
            limit: Maximum number of trades to return (default: 100)
            before: Cursor for pagination (trade ID)
        """
        params: Dict[str, Any] = {"limit": limit}
        if before:
            params["before"] = before

        data = self._client.get(f"/api/trades/{market_id}", params=params)
        trades_data = data.get("trades", data) if isinstance(data, dict) else data
        return [Trade.model_validate(t) for t in trades_data]

    def get_ohlcv(
        self,
        market_id: str,
        interval: str = "1h",
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[OHLCV]:
        """Get OHLCV (candlestick) data for a market

        Args:
            market_id: Market identifier
            interval: Candlestick interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Maximum number of candles to return (default: 100)
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        """
        params: Dict[str, Any] = {
            "interval": interval,
            "limit": limit,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        data = self._client.get(f"/api/ohlcv/{market_id}", params=params)
        ohlcv_data = data.get("ohlcv", data) if isinstance(data, dict) else data
        return [OHLCV.model_validate(o) for o in ohlcv_data]


class AsyncMarketsEndpoint:
    """Async public market data endpoints"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_assets(self) -> List[Asset]:
        """Get all available assets"""
        data = await self._client.get("/api/assets")
        assets_data = data.get("assets", data) if isinstance(data, dict) else data
        return [Asset.model_validate(a) for a in assets_data]

    async def get_asset(self, asset_id: str) -> Asset:
        """Get a specific asset by ID"""
        data = await self._client.get(f"/api/assets/{asset_id}")
        return Asset.model_validate(data)

    async def get_markets(self) -> List[Market]:
        """Get all available markets"""
        data = await self._client.get("/api/markets")
        markets_data = data.get("markets", data) if isinstance(data, dict) else data
        return [Market.model_validate(m) for m in markets_data]

    async def get_market(self, market_id: str) -> Market:
        """Get a specific market by ID"""
        data = await self._client.get(f"/api/markets/{market_id}")
        return Market.model_validate(data)

    async def get_tickers(self) -> List[Ticker]:
        """Get tickers for all markets"""
        data = await self._client.get("/api/tickers")
        tickers_data = data.get("tickers", data) if isinstance(data, dict) else data
        return [Ticker.model_validate(t) for t in tickers_data]

    async def get_ticker(self, market_id: str) -> Ticker:
        """Get ticker for a specific market"""
        data = await self._client.get(f"/api/tickers/{market_id}")
        return Ticker.model_validate(data)

    async def get_orderbook(self, market_id: str, depth: int = 50) -> OrderBook:
        """Get orderbook for a market"""
        data = await self._client.get(f"/api/orderbook/{market_id}", params={"depth": depth})
        return OrderBook.model_validate(data)

    async def get_trades(
        self,
        market_id: str,
        limit: int = 100,
        before: Optional[str] = None,
    ) -> List[Trade]:
        """Get recent trades for a market"""
        params: Dict[str, Any] = {"limit": limit}
        if before:
            params["before"] = before

        data = await self._client.get(f"/api/trades/{market_id}", params=params)
        trades_data = data.get("trades", data) if isinstance(data, dict) else data
        return [Trade.model_validate(t) for t in trades_data]

    async def get_ohlcv(
        self,
        market_id: str,
        interval: str = "1h",
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[OHLCV]:
        """Get OHLCV (candlestick) data for a market"""
        params: Dict[str, Any] = {
            "interval": interval,
            "limit": limit,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        data = await self._client.get(f"/api/ohlcv/{market_id}", params=params)
        ohlcv_data = data.get("ohlcv", data) if isinstance(data, dict) else data
        return [OHLCV.model_validate(o) for o in ohlcv_data]
