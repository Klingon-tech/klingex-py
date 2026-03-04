"""
KlingEx WebSocket Client
"""

import asyncio
import json
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import websockets
from websockets.client import WebSocketClientProtocol

from klingex.http import KlingExError


class WebSocketChannel(str, Enum):
    """Available WebSocket channels"""
    TICKER = "ticker"
    ORDERBOOK = "orderbook"
    TRADES = "trades"
    OHLCV = "ohlcv"
    USER_ORDERS = "user:orders"
    USER_TRADES = "user:trades"
    USER_BALANCES = "user:balances"
    USER_ACCOUNT = "user:account"


MessageHandler = Callable[[Dict[str, Any]], None]
AsyncMessageHandler = Callable[[Dict[str, Any]], Any]


class KlingExWebSocket:
    """WebSocket client for real-time KlingEx data and trading"""

    DEFAULT_WS_URL = "wss://ws.klingex.io"

    def __init__(
        self,
        api_key: Optional[str] = None,
        ws_url: Optional[str] = None,
        on_order_result: Optional[AsyncMessageHandler] = None,
        on_cancel_result: Optional[AsyncMessageHandler] = None,
        on_user_trade: Optional[AsyncMessageHandler] = None,
        on_account_event: Optional[AsyncMessageHandler] = None,
    ):
        self.api_key = api_key
        self.ws_url = ws_url or self.DEFAULT_WS_URL
        self._ws: Optional[WebSocketClientProtocol] = None
        self._subscriptions: Set[str] = set()
        self._handlers: Dict[str, List[AsyncMessageHandler]] = {}
        self._running = False
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 60.0
        self._pending_requests: Dict[str, asyncio.Future] = {}

        # Optional callbacks for trading events
        self.on_order_result = on_order_result
        self.on_cancel_result = on_cancel_result
        self.on_user_trade = on_user_trade
        self.on_account_event = on_account_event

    async def connect(self) -> None:
        """Establish WebSocket connection"""
        self._running = True
        await self._connect()

    async def _connect(self) -> None:
        """Internal connection handler with reconnection logic"""
        while self._running:
            try:
                self._ws = await websockets.connect(self.ws_url)
                self._reconnect_delay = 1.0  # Reset delay on successful connection

                # Authenticate if API key provided
                if self.api_key:
                    await self._authenticate()

                # Resubscribe to channels
                for subscription in self._subscriptions:
                    await self._send_subscribe(subscription)

                # Start message loop
                await self._message_loop()

            except websockets.ConnectionClosed:
                self._reject_pending_requests("Connection closed")
                if self._running:
                    await self._handle_reconnect()
            except Exception as e:
                self._reject_pending_requests("Connection error")
                if self._running:
                    await self._handle_reconnect()

    async def _handle_reconnect(self) -> None:
        """Handle reconnection with exponential backoff"""
        await asyncio.sleep(self._reconnect_delay)
        self._reconnect_delay = min(
            self._reconnect_delay * 2,
            self._max_reconnect_delay,
        )

    async def _authenticate(self) -> None:
        """Send authentication message"""
        if not self._ws:
            return

        auth_message = {
            "type": "auth",
            "apiKey": self.api_key,
        }
        await self._ws.send(json.dumps(auth_message))

    async def _send(self, data: dict) -> None:
        """Send a JSON message over the WebSocket"""
        if not self._ws:
            raise KlingExError("WebSocket not connected")
        await self._ws.send(json.dumps(data))

    async def _send_request(
        self, action: str, data: dict, timeout: float = 10.0
    ) -> dict:
        """Send a request and wait for its correlated response.

        Uses requestId to match the response to this specific request.
        """
        request_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self._pending_requests[request_id] = future

        await self._send({**data, "action": action, "requestId": request_id})

        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            self._pending_requests.pop(request_id, None)

    def _reject_pending_requests(self, reason: str) -> None:
        """Reject all pending request futures (e.g. on disconnect)"""
        for request_id, future in list(self._pending_requests.items()):
            if not future.done():
                future.set_exception(KlingExError(reason))
        self._pending_requests.clear()

    async def _message_loop(self) -> None:
        """Process incoming WebSocket messages"""
        if not self._ws:
            return

        async for message in self._ws:
            try:
                data = json.loads(message)
                await self._dispatch_message(data)
            except json.JSONDecodeError:
                continue

    async def _dispatch_message(self, data: Dict[str, Any]) -> None:
        """Route message to appropriate handlers"""
        msg_type = data.get("type")

        # Handle request-response correlation for trading results
        if msg_type in ("order_result", "cancel_result"):
            request_id = data.get("requestId")
            if request_id and request_id in self._pending_requests:
                future = self._pending_requests.pop(request_id)
                if not future.done():
                    future.set_result(data)

            # Also dispatch to dedicated callbacks
            if msg_type == "order_result" and self.on_order_result:
                await self._call_handler(self.on_order_result, data)
            elif msg_type == "cancel_result" and self.on_cancel_result:
                await self._call_handler(self.on_cancel_result, data)
            return

        # Dispatch to on_user_trade callback
        if msg_type == "user_trade" and self.on_user_trade:
            await self._call_handler(self.on_user_trade, data)

        # Dispatch to on_account_event callback
        if msg_type == "account_event" and self.on_account_event:
            await self._call_handler(self.on_account_event, data)

        channel = data.get("channel") or msg_type
        if not channel:
            return

        # Call channel-specific handlers
        if channel in self._handlers:
            for handler in self._handlers[channel]:
                await self._call_handler(handler, data)

        # Call wildcard handlers
        if "*" in self._handlers:
            for handler in self._handlers["*"]:
                await self._call_handler(handler, data)

    async def _call_handler(
        self, handler: AsyncMessageHandler, data: Dict[str, Any]
    ) -> None:
        """Safely call a handler, supporting both sync and async"""
        try:
            result = handler(data)
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            pass  # Don't let handler errors break the loop

    async def _send_subscribe(self, channel: str) -> None:
        """Send subscription message"""
        if not self._ws:
            return

        message = {
            "type": "subscribe",
            "channel": channel,
        }
        await self._ws.send(json.dumps(message))

    async def _send_unsubscribe(self, channel: str) -> None:
        """Send unsubscribe message"""
        if not self._ws:
            return

        message = {
            "type": "unsubscribe",
            "channel": channel,
        }
        await self._ws.send(json.dumps(message))

    # =========================================================================
    # Trading Methods
    # =========================================================================

    async def place_order(
        self,
        symbol: str,
        trading_pair_id: int,
        side: str,
        quantity: str,
        price: str,
        raw_values: bool = True,
    ) -> dict:
        """Place an order via WebSocket.

        Args:
            symbol: Trading pair symbol (e.g. "BTC-USDT")
            trading_pair_id: Trading pair ID
            side: "BUY" or "SELL"
            quantity: Order quantity
            price: Order price (use "0" for market orders)
            raw_values: If True, quantity/price are in base units

        Returns:
            Order result dict with 'success', 'orderId', etc.

        Raises:
            KlingExError: If the order fails or times out
        """
        result = await self._send_request("place_order", {
            "symbol": symbol,
            "tradingPairId": trading_pair_id,
            "side": side,
            "quantity": quantity,
            "price": price,
            "rawValues": raw_values,
        })
        if not result.get("success"):
            raise KlingExError(result.get("error", "Order failed"))
        return result

    async def cancel_order(
        self, order_id: str, trading_pair_id: int
    ) -> dict:
        """Cancel an order via WebSocket.

        Args:
            order_id: The order UUID to cancel
            trading_pair_id: Trading pair ID

        Returns:
            Cancel result dict with 'success', etc.

        Raises:
            KlingExError: If the cancellation fails or times out
        """
        result = await self._send_request("cancel_order", {
            "orderId": order_id,
            "tradingPairId": trading_pair_id,
        })
        if not result.get("success"):
            raise KlingExError(result.get("error", "Cancel failed"))
        return result

    # =========================================================================
    # Subscription Methods
    # =========================================================================

    async def subscribe(
        self,
        channel: str,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to a channel"""
        self._subscriptions.add(channel)

        if handler:
            if channel not in self._handlers:
                self._handlers[channel] = []
            self._handlers[channel].append(handler)

        if self._ws:
            await self._send_subscribe(channel)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel"""
        self._subscriptions.discard(channel)
        self._handlers.pop(channel, None)

        if self._ws:
            await self._send_unsubscribe(channel)

    def on(self, channel: str, handler: AsyncMessageHandler) -> None:
        """Register a handler for a channel"""
        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

    def off(self, channel: str, handler: Optional[AsyncMessageHandler] = None) -> None:
        """Remove handler(s) for a channel"""
        if handler and channel in self._handlers:
            self._handlers[channel] = [h for h in self._handlers[channel] if h != handler]
        elif channel in self._handlers:
            del self._handlers[channel]

    async def subscribe_ticker(
        self,
        market_id: str,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to ticker updates for a market"""
        channel = f"ticker:{market_id}"
        await self.subscribe(channel, handler)

    async def subscribe_orderbook(
        self,
        market_id: str,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to orderbook updates for a market"""
        channel = f"orderbook:{market_id}"
        await self.subscribe(channel, handler)

    async def subscribe_trades(
        self,
        market_id: str,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to trade updates for a market"""
        channel = f"trades:{market_id}"
        await self.subscribe(channel, handler)

    async def subscribe_user_orders(
        self,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to user order updates (requires authentication)"""
        await self.subscribe("user:orders", handler)

    async def subscribe_user_trades(
        self,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to user trade updates (requires authentication)"""
        await self.subscribe("user:trades", handler)

    async def subscribe_user_balances(
        self,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to user balance updates (requires authentication)"""
        await self.subscribe("user:balances", handler)

    async def subscribe_account(
        self,
        handler: Optional[AsyncMessageHandler] = None,
    ) -> None:
        """Subscribe to account security events (requires authentication)

        Receives events such as login alerts, password changes, API key
        creation/revocation, and 2FA changes.
        """
        await self.subscribe("user:account", handler)

    async def close(self) -> None:
        """Close WebSocket connection"""
        self._running = False
        self._reject_pending_requests("Connection closed by client")
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def __aenter__(self) -> "KlingExWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
