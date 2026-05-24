"""Orders endpoint - order placement, cancellation, history."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.http import KlingExError
from klingex.types import (
    Order,
    OrderResponse,
    CancelOrderResponse,
    OrderSide,
    CancelAllOrdersResponse,
    OrderHistory,
    OrdersHistoryResponse,
)

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


def _normalize_side(side: Any) -> str:
    if isinstance(side, OrderSide):
        return side.value
    return str(side)


def _build_submit_payload(
    symbol: str,
    trading_pair_id: int,
    side: Any,
    quantity: str,
    price: str,
    raw_values: bool,
) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "tradingPairId": trading_pair_id,
        "side": _normalize_side(side),
        "quantity": quantity,
        "price": price,
        "rawValues": raw_values,
    }


def _build_history_params(
    trading_pair_id: Optional[int],
    status: Optional[str],
    market: Optional[str],
    side: Optional[Any],
    type_: Optional[str],
    search: Optional[str],
    from_: Optional[str],
    to: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if trading_pair_id is not None:
        params["tradingPairId"] = trading_pair_id
    if status is not None:
        params["status"] = status
    if market is not None:
        params["market"] = market
    if side is not None:
        params["side"] = _normalize_side(side)
    if type_ is not None:
        params["type"] = type_
    if search is not None:
        params["search"] = search
    if from_ is not None:
        params["from"] = from_
    if to is not None:
        params["to"] = to
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return params


class OrdersEndpoint:
    """Order management endpoints (synchronous)."""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def submit_order(
        self,
        symbol: str,
        trading_pair_id: int,
        side: OrderSide,
        quantity: str,
        price: str,
        raw_values: bool = False,
    ) -> OrderResponse:
        """Submit a new limit order.

        Args:
            symbol: Trading pair symbol, e.g. ``"BTC-USDT"``.
            trading_pair_id: Trading pair ID (required for partition routing).
            side: ``OrderSide.BUY`` or ``OrderSide.SELL``.
            quantity: Order quantity. If ``raw_values=False`` (default)
                this is interpreted as a human-readable decimal string
                (e.g. ``"0.1"``); if ``raw_values=True`` it is the raw
                integer base-unit amount (e.g. ``"10000000"`` for 0.1 BTC).
            price: Limit price. Same units convention as ``quantity``.
                Use ``"0"`` for a market order.
            raw_values: See above.

        Returns:
            :class:`OrderResponse` with ``message`` and ``order_id``.
        """
        response = self._client.post(
            "/api/submit-order",
            data=_build_submit_payload(
                symbol, trading_pair_id, side, quantity, price, raw_values
            ),
            authenticated=True,
        )
        return OrderResponse.model_validate(response)

    def cancel_order(self, order_id: str, trading_pair_id: int) -> CancelOrderResponse:
        """Cancel a single active order."""
        response = self._client.post(
            "/api/cancel-order",
            data={"orderId": order_id, "tradingPairId": trading_pair_id},
            authenticated=True,
        )
        return CancelOrderResponse.model_validate(response)

    def cancel_all_orders(self, trading_pair_id: int) -> CancelAllOrdersResponse:
        """Cancel every open order on a single trading pair.

        Requires the ``trade`` scope on the API key.
        """
        response = self._client.post(
            "/api/cancel-all-orders",
            data={"tradingPairId": trading_pair_id},
            authenticated=True,
        )
        return CancelAllOrdersResponse.model_validate(response)

    def get_orders(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Order]:
        """Fetch active user orders.

        Valid ``status`` values: ``pending``, ``partial``, ``filled``,
        ``cancelled``, ``rejected``. The backend does not have a separate
        ``open`` state — newly placed orders are ``pending`` until they
        partially fill (``partial``) or fully fill (``filled``).
        """
        params: Dict[str, Any] = {"limit": limit}
        if trading_pair_id is not None:
            params["tradingPairId"] = trading_pair_id
        if status is not None:
            params["status"] = status

        response = self._client.get("/api/user-orders", params=params, authenticated=True)
        orders_data = response.get("orders", response) if isinstance(response, dict) else response
        return [Order.model_validate(o) for o in orders_data]

    def get_open_orders(self, trading_pair_id: Optional[int] = None) -> List[Order]:
        """Return all open (pending or partially-filled) orders.

        The backend has no ``open`` status; this method merges results of
        ``status=pending`` and ``status=partial`` for convenience.
        """
        pending = self.get_orders(trading_pair_id=trading_pair_id, status="pending")
        partial = self.get_orders(trading_pair_id=trading_pair_id, status="partial")
        return pending + partial

    def get_orders_history(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        market: Optional[str] = None,
        side: Optional[OrderSide] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> OrdersHistoryResponse:
        """Fetch paginated order history (including filled/cancelled).

        Args:
            trading_pair_id: Filter by trading pair.
            status: ``pending``, ``partial``, ``filled``, ``cancelled``, ``rejected``.
            market: Market string ``BASE-QUOTE`` or ``BASE/QUOTE``.
            side: ``OrderSide.BUY`` / ``OrderSide.SELL`` or string.
            type: ``limit`` or ``market``.
            search: Free-text search.
            from_date: Inclusive start date, ``YYYY-MM-DD``.
            to_date: Inclusive end date (end-of-day), ``YYYY-MM-DD``.
            limit: 1-100, default 50.
            offset: Pagination offset.

        Requires the ``read`` scope.
        """
        params = _build_history_params(
            trading_pair_id, status, market, side, type, search,
            from_date, to_date, limit, offset,
        )
        response = self._client.get(
            "/api/orders-history", params=params, authenticated=True
        )
        return OrdersHistoryResponse.model_validate(response)


class AsyncOrdersEndpoint:
    """Order management endpoints (async)."""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def submit_order(
        self,
        symbol: str,
        trading_pair_id: int,
        side: OrderSide,
        quantity: str,
        price: str,
        raw_values: bool = False,
    ) -> OrderResponse:
        response = await self._client.post(
            "/api/submit-order",
            data=_build_submit_payload(
                symbol, trading_pair_id, side, quantity, price, raw_values
            ),
            authenticated=True,
        )
        return OrderResponse.model_validate(response)

    async def cancel_order(self, order_id: str, trading_pair_id: int) -> CancelOrderResponse:
        response = await self._client.post(
            "/api/cancel-order",
            data={"orderId": order_id, "tradingPairId": trading_pair_id},
            authenticated=True,
        )
        return CancelOrderResponse.model_validate(response)

    async def cancel_all_orders(self, trading_pair_id: int) -> CancelAllOrdersResponse:
        response = await self._client.post(
            "/api/cancel-all-orders",
            data={"tradingPairId": trading_pair_id},
            authenticated=True,
        )
        return CancelAllOrdersResponse.model_validate(response)

    async def get_orders(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Order]:
        params: Dict[str, Any] = {"limit": limit}
        if trading_pair_id is not None:
            params["tradingPairId"] = trading_pair_id
        if status is not None:
            params["status"] = status
        response = await self._client.get(
            "/api/user-orders", params=params, authenticated=True
        )
        orders_data = response.get("orders", response) if isinstance(response, dict) else response
        return [Order.model_validate(o) for o in orders_data]

    async def get_open_orders(self, trading_pair_id: Optional[int] = None) -> List[Order]:
        pending = await self.get_orders(trading_pair_id=trading_pair_id, status="pending")
        partial = await self.get_orders(trading_pair_id=trading_pair_id, status="partial")
        return pending + partial

    async def get_orders_history(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        market: Optional[str] = None,
        side: Optional[OrderSide] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> OrdersHistoryResponse:
        params = _build_history_params(
            trading_pair_id, status, market, side, type, search,
            from_date, to_date, limit, offset,
        )
        response = await self._client.get(
            "/api/orders-history", params=params, authenticated=True
        )
        return OrdersHistoryResponse.model_validate(response)
