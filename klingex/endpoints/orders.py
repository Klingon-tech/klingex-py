"""
Orders Endpoint - Order management
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Order, OrderResponse, OrderSide, OrderType, TimeInForce

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class OrdersEndpoint:
    """Order management endpoints (authenticated)"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def submit_order(
        self,
        market_id: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: Optional[TimeInForce] = None,
        raw_values: bool = False,
    ) -> OrderResponse:
        """Submit a new order

        Args:
            market_id: Market identifier (e.g., "BTC-USDT")
            side: Order side (buy or sell)
            order_type: Order type (limit or market)
            quantity: Order quantity (human-readable by default, e.g., "0.5" for 0.5 BTC)
            price: Order price (required for limit orders, human-readable by default)
            time_in_force: Time in force (gtc, ioc, fok)
            raw_values: If True, quantity/price are in raw base units (e.g., satoshis)
                       If False (default), values are human-readable (e.g., "1.5" = 1.5 BTC)
        """
        data: Dict[str, Any] = {
            "marketId": market_id,
            "side": side.value if isinstance(side, OrderSide) else side,
            "type": order_type.value if isinstance(order_type, OrderType) else order_type,
            "quantity": quantity,
        }

        if price is not None:
            data["price"] = price

        if time_in_force is not None:
            data["timeInForce"] = (
                time_in_force.value if isinstance(time_in_force, TimeInForce) else time_in_force
            )

        if raw_values:
            data["rawValues"] = True

        result = self._client.post("/api/orders/submit", data=data, authenticated=True)
        return OrderResponse.model_validate(result)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order

        Args:
            order_id: Order ID to cancel
        """
        return self._client.delete(f"/api/orders/{order_id}", authenticated=True)

    def cancel_all_orders(self, market_id: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all open orders

        Args:
            market_id: Optional market ID to cancel orders for specific market only
        """
        params = {"marketId": market_id} if market_id else None
        return self._client.delete("/api/orders", params=params, authenticated=True)

    def get_order(self, order_id: str) -> Order:
        """Get a specific order by ID

        Args:
            order_id: Order ID
        """
        data = self._client.get(f"/api/orders/{order_id}", authenticated=True)
        return Order.model_validate(data)

    def get_open_orders(
        self,
        market_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        """Get all open orders

        Args:
            market_id: Optional market ID to filter by
            limit: Maximum number of orders to return
            offset: Pagination offset
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if market_id:
            params["marketId"] = market_id

        data = self._client.get("/api/orders/open", params=params, authenticated=True)
        orders_data = data.get("orders", data) if isinstance(data, dict) else data
        return [Order.model_validate(o) for o in orders_data]

    def get_order_history(
        self,
        market_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        """Get order history

        Args:
            market_id: Optional market ID to filter by
            status: Optional status to filter by (filled, cancelled)
            limit: Maximum number of orders to return
            offset: Pagination offset
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if market_id:
            params["marketId"] = market_id
        if status:
            params["status"] = status

        data = self._client.get("/api/orders/history", params=params, authenticated=True)
        orders_data = data.get("orders", data) if isinstance(data, dict) else data
        return [Order.model_validate(o) for o in orders_data]


class AsyncOrdersEndpoint:
    """Async order management endpoints (authenticated)"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def submit_order(
        self,
        market_id: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: Optional[TimeInForce] = None,
        raw_values: bool = False,
    ) -> OrderResponse:
        """Submit a new order"""
        data: Dict[str, Any] = {
            "marketId": market_id,
            "side": side.value if isinstance(side, OrderSide) else side,
            "type": order_type.value if isinstance(order_type, OrderType) else order_type,
            "quantity": quantity,
        }

        if price is not None:
            data["price"] = price

        if time_in_force is not None:
            data["timeInForce"] = (
                time_in_force.value if isinstance(time_in_force, TimeInForce) else time_in_force
            )

        if raw_values:
            data["rawValues"] = True

        result = await self._client.post("/api/orders/submit", data=data, authenticated=True)
        return OrderResponse.model_validate(result)

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        return await self._client.delete(f"/api/orders/{order_id}", authenticated=True)

    async def cancel_all_orders(self, market_id: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all open orders"""
        params = {"marketId": market_id} if market_id else None
        return await self._client.delete("/api/orders", params=params, authenticated=True)

    async def get_order(self, order_id: str) -> Order:
        """Get a specific order by ID"""
        data = await self._client.get(f"/api/orders/{order_id}", authenticated=True)
        return Order.model_validate(data)

    async def get_open_orders(
        self,
        market_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        """Get all open orders"""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if market_id:
            params["marketId"] = market_id

        data = await self._client.get("/api/orders/open", params=params, authenticated=True)
        orders_data = data.get("orders", data) if isinstance(data, dict) else data
        return [Order.model_validate(o) for o in orders_data]

    async def get_order_history(
        self,
        market_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        """Get order history"""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if market_id:
            params["marketId"] = market_id
        if status:
            params["status"] = status

        data = await self._client.get("/api/orders/history", params=params, authenticated=True)
        orders_data = data.get("orders", data) if isinstance(data, dict) else data
        return [Order.model_validate(o) for o in orders_data]
