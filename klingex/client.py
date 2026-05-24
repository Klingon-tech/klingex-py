"""KlingEx Client - main SDK entry points."""

from typing import Optional

from klingex.http import HttpClient, AsyncHttpClient
from klingex.endpoints.markets import MarketsEndpoint, AsyncMarketsEndpoint
from klingex.endpoints.orders import OrdersEndpoint, AsyncOrdersEndpoint
from klingex.endpoints.wallet import WalletEndpoint, AsyncWalletEndpoint
from klingex.endpoints.invoices import InvoicesEndpoint, AsyncInvoicesEndpoint
from klingex.endpoints.withdrawals import WithdrawalsEndpoint, AsyncWithdrawalsEndpoint
from klingex.endpoints.pools import PoolsEndpoint, AsyncPoolsEndpoint
from klingex.endpoints.mining_pool import MiningPoolEndpoint, AsyncMiningPoolEndpoint
from klingex.endpoints.gift_codes import GiftCodesEndpoint, AsyncGiftCodesEndpoint


class KlingEx:
    """
    KlingEx Exchange API Client (synchronous).

    Example::

        from klingex import KlingEx, OrderSide

        # Public endpoints
        with KlingEx() as client:
            markets = client.markets.get_markets()

        # Authenticated endpoints
        with KlingEx(api_key="...") as client:
            balances = client.wallet.get_balances()
            order = client.orders.submit_order(
                symbol="BTC-USDT",
                trading_pair_id=1,
                side=OrderSide.BUY,
                quantity="0.1",
                price="50000",
            )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self._http = HttpClient(api_key=api_key, base_url=base_url, timeout=timeout)

        self.markets = MarketsEndpoint(self._http)
        self.orders = OrdersEndpoint(self._http)
        self.wallet = WalletEndpoint(self._http)
        self.invoices = InvoicesEndpoint(self._http)
        self.withdrawals = WithdrawalsEndpoint(self._http)
        self.pools = PoolsEndpoint(self._http)
        self.mining_pool = MiningPoolEndpoint(self._http)
        self.gift_codes = GiftCodesEndpoint(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "KlingEx":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class AsyncKlingEx:
    """
    KlingEx Exchange API Client (async).

    Example::

        import asyncio
        from klingex import AsyncKlingEx

        async def main():
            async with AsyncKlingEx(api_key="...") as client:
                markets = await client.markets.get_markets()
                balances = await client.wallet.get_balances()

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self._http = AsyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)

        self.markets = AsyncMarketsEndpoint(self._http)
        self.orders = AsyncOrdersEndpoint(self._http)
        self.wallet = AsyncWalletEndpoint(self._http)
        self.invoices = AsyncInvoicesEndpoint(self._http)
        self.withdrawals = AsyncWithdrawalsEndpoint(self._http)
        self.pools = AsyncPoolsEndpoint(self._http)
        self.mining_pool = AsyncMiningPoolEndpoint(self._http)
        self.gift_codes = AsyncGiftCodesEndpoint(self._http)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> "AsyncKlingEx":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
