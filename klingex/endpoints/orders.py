"""
Orders Endpoint - Order management
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Order, OrderResponse, CancelOrderResponse, OrderSide, OrderType

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class OrdersEndpoint:
    """Order management endpoints"""

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
        slippage: Optional[float] = None,
    ) -> OrderResponse:
        """Submit a new order

        Args:
            symbol: Trading pair symbol (e.g., "BTC-USDT")
            trading_pair_id: Trading pair ID
            side: Order side (BUY or SELL)
            quantity: Order quantity (human-readable if raw_values=False)
            price: Order price (human-readable if raw_values=False, "0" for market orders)
            raw_values: If True, quantity/price are in base units. If False, human-readable
            slippage: Slippage tolerance for market orders (0-1, e.g., 0.01 for 1%)
        """
        data: Dict[str, Any] = {
            "symbol": symbol,
            "tradingPairId": trading_pair_id,
            "side": side.value if isinstance(side, OrderSide) else side,
            "quantity": quantity,
            "price": price,
            "rawValues": raw_values,
        }
        if slippage is not None:
            data["slippage"] = slippage

        response = self._client.post("/api/submit-order", data=data, authenticated=True)
        return OrderResponse.model_validate(response)

    def cancel_order(self, order_id: str, trading_pair_id: int) -> CancelOrderResponse:
        """Cancel an active order

        Args:
            order_id: Order ID to cancel
            trading_pair_id: Trading pair ID
        """
        data = {
            "orderId": order_id,
            "tradingPairId": trading_pair_id,
        }
        response = self._client.post("/api/cancel-order", data=data, authenticated=True)
        return CancelOrderResponse.model_validate(response)

    def get_orders(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Order]:
        """Get user orders

        Args:
            trading_pair_id: Filter by trading pair ID
            status: Filter by order status
            limit: Maximum number of orders (default: 50)
        """
        params: Dict[str, Any] = {"limit": limit}
        if trading_pair_id:
            params["tradingPairId"] = trading_pair_id
        if status:
            params["status"] = status

        response = self._client.get("/api/user-orders", params=params, authenticated=True)
        orders_data = response.get("orders", response) if isinstance(response, dict) else response
        return [Order.model_validate(o) for o in orders_data]

    def get_open_orders(self, trading_pair_id: Optional[int] = None) -> List[Order]:
        """Get open orders

        Args:
            trading_pair_id: Filter by trading pair ID
        """
        return self.get_orders(trading_pair_id=trading_pair_id, status="open")


class AsyncOrdersEndpoint:
    """Async order management endpoints"""

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
        slippage: Optional[float] = None,
    ) -> OrderResponse:
        """Submit a new order"""
        data: Dict[str, Any] = {
            "symbol": symbol,
            "tradingPairId": trading_pair_id,
            "side": side.value if isinstance(side, OrderSide) else side,
            "quantity": quantity,
            "price": price,
            "rawValues": raw_values,
        }
        if slippage is not None:
            data["slippage"] = slippage

        response = await self._client.post("/api/submit-order", data=data, authenticated=True)
        return OrderResponse.model_validate(response)

    async def cancel_order(self, order_id: str, trading_pair_id: int) -> CancelOrderResponse:
        """Cancel an active order"""
        data = {
            "orderId": order_id,
            "tradingPairId": trading_pair_id,
        }
        response = await self._client.post("/api/cancel-order", data=data, authenticated=True)
        return CancelOrderResponse.model_validate(response)

    async def get_orders(
        self,
        trading_pair_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Order]:
        """Get user orders"""
        params: Dict[str, Any] = {"limit": limit}
        if trading_pair_id:
            params["tradingPairId"] = trading_pair_id
        if status:
            params["status"] = status

        response = await self._client.get("/api/user-orders", params=params, authenticated=True)
        orders_data = response.get("orders", response) if isinstance(response, dict) else response
        return [Order.model_validate(o) for o in orders_data]

    async def get_open_orders(self, trading_pair_id: Optional[int] = None) -> List[Order]:
        """Get open orders"""
        return await self.get_orders(trading_pair_id=trading_pair_id, status="open")
