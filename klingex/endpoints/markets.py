"""
Markets Endpoint - Public market data
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Asset, Market, Ticker, OrderBook, OHLCV

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

    def get_markets(self) -> List[Market]:
        """Get all available markets"""
        data = self._client.get("/api/markets")
        return [Market.model_validate(m) for m in data]

    def get_market(self, market_id: int) -> Market:
        """Get a specific market by ID"""
        markets = self.get_markets()
        for market in markets:
            if market.id == market_id:
                return market
        raise ValueError(f"Market {market_id} not found")

    def get_tickers(self) -> List[Ticker]:
        """Get tickers for all markets (CMC/CoinGecko format)"""
        data = self._client.get("/api/tickers")
        return [Ticker.model_validate(t) for t in data]

    def get_ticker(self, ticker_id: str) -> Ticker:
        """Get ticker for a specific market

        Args:
            ticker_id: Ticker ID like "BTC_USDT"
        """
        tickers = self.get_tickers()
        for ticker in tickers:
            if ticker.ticker_id == ticker_id:
                return ticker
        raise ValueError(f"Ticker {ticker_id} not found")

    def get_orderbook(self, market_id: int) -> OrderBook:
        """Get orderbook for a market

        Args:
            market_id: Trading pair ID
        """
        data = self._client.get("/api/orderbook", params={"marketId": market_id, "isCmc": "false"})
        return OrderBook.model_validate(data)

    def get_ohlcv(
        self,
        market_id: int,
        timeframe: str = "5m",
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
    ) -> List[OHLCV]:
        """Get OHLCV (candlestick) data for a market

        Args:
            market_id: Trading pair ID
            timeframe: Candlestick interval (1m, 5m, 15m, 30m, 1h, 4h, 1D)
            limit: Maximum number of candles to return
            start_date: ISO 8601 date string for start time
        """
        params: Dict[str, Any] = {
            "marketId": market_id,
            "timeframe": timeframe,
        }
        if limit:
            params["limit"] = limit
        if start_date:
            params["startDate"] = start_date

        data = self._client.get("/api/ohlcv", params=params)
        return [OHLCV.model_validate(o) for o in data]


class AsyncMarketsEndpoint:
    """Async public market data endpoints"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def get_assets(self) -> List[Asset]:
        """Get all available assets"""
        data = await self._client.get("/api/assets")
        assets_data = data.get("assets", data) if isinstance(data, dict) else data
        return [Asset.model_validate(a) for a in assets_data]

    async def get_markets(self) -> List[Market]:
        """Get all available markets"""
        data = await self._client.get("/api/markets")
        return [Market.model_validate(m) for m in data]

    async def get_market(self, market_id: int) -> Market:
        """Get a specific market by ID"""
        markets = await self.get_markets()
        for market in markets:
            if market.id == market_id:
                return market
        raise ValueError(f"Market {market_id} not found")

    async def get_tickers(self) -> List[Ticker]:
        """Get tickers for all markets (CMC/CoinGecko format)"""
        data = await self._client.get("/api/tickers")
        return [Ticker.model_validate(t) for t in data]

    async def get_ticker(self, ticker_id: str) -> Ticker:
        """Get ticker for a specific market"""
        tickers = await self.get_tickers()
        for ticker in tickers:
            if ticker.ticker_id == ticker_id:
                return ticker
        raise ValueError(f"Ticker {ticker_id} not found")

    async def get_orderbook(self, market_id: int) -> OrderBook:
        """Get orderbook for a market"""
        data = await self._client.get("/api/orderbook", params={"marketId": market_id, "isCmc": "false"})
        return OrderBook.model_validate(data)

    async def get_ohlcv(
        self,
        market_id: int,
        timeframe: str = "5m",
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
    ) -> List[OHLCV]:
        """Get OHLCV (candlestick) data for a market"""
        params: Dict[str, Any] = {
            "marketId": market_id,
            "timeframe": timeframe,
        }
        if limit:
            params["limit"] = limit
        if start_date:
            params["startDate"] = start_date

        data = await self._client.get("/api/ohlcv", params=params)
        return [OHLCV.model_validate(o) for o in data]
