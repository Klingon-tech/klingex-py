"""
KlingEx Client - Main SDK entry point
"""

from typing import Optional

from klingex.http import HttpClient, AsyncHttpClient
from klingex.endpoints.markets import MarketsEndpoint, AsyncMarketsEndpoint
from klingex.endpoints.orders import OrdersEndpoint, AsyncOrdersEndpoint
from klingex.endpoints.wallet import WalletEndpoint, AsyncWalletEndpoint
from klingex.endpoints.invoices import InvoicesEndpoint, AsyncInvoicesEndpoint


class KlingEx:
    """
    KlingEx Exchange API Client

    Synchronous client for interacting with the KlingEx Exchange API.

    Example:
        ```python
        from klingex import KlingEx

        # Public endpoints (no auth required)
        client = KlingEx()
        markets = client.markets.get_markets()
        ticker = client.markets.get_ticker("BTC-USDT")

        # Authenticated endpoints
        client = KlingEx(api_key="your_key", api_secret="your_secret")
        balances = client.wallet.get_balances()
        order = client.orders.submit_order(
            market_id="BTC-USDT",
            side="buy",
            order_type="limit",
            quantity="0.1",
            price="50000"
        )
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize KlingEx client.

        Args:
            api_key: API key for authenticated endpoints
            api_secret: API secret for authenticated endpoints
            base_url: Base URL for the API (default: https://api.klingex.io)
            timeout: Request timeout in seconds (default: 30)
        """
        self._http = HttpClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            timeout=timeout,
        )

        # Initialize endpoint modules
        self.markets = MarketsEndpoint(self._http)
        self.orders = OrdersEndpoint(self._http)
        self.wallet = WalletEndpoint(self._http)
        self.invoices = InvoicesEndpoint(self._http)

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "KlingEx":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class AsyncKlingEx:
    """
    KlingEx Exchange API Client (Async)

    Asynchronous client for interacting with the KlingEx Exchange API.

    Example:
        ```python
        import asyncio
        from klingex import AsyncKlingEx

        async def main():
            async with AsyncKlingEx(api_key="key", api_secret="secret") as client:
                markets = await client.markets.get_markets()
                balances = await client.wallet.get_balances()

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize async KlingEx client.

        Args:
            api_key: API key for authenticated endpoints
            api_secret: API secret for authenticated endpoints
            base_url: Base URL for the API (default: https://api.klingex.io)
            timeout: Request timeout in seconds (default: 30)
        """
        self._http = AsyncHttpClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            timeout=timeout,
        )

        # Initialize endpoint modules
        self.markets = AsyncMarketsEndpoint(self._http)
        self.orders = AsyncOrdersEndpoint(self._http)
        self.wallet = AsyncWalletEndpoint(self._http)
        self.invoices = AsyncInvoicesEndpoint(self._http)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> "AsyncKlingEx":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
