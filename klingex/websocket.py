"""
KlingEx WebSocket Client
"""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum

import websockets
from websockets.client import WebSocketClientProtocol


class WebSocketChannel(str, Enum):
    """Available WebSocket channels"""
    TICKER = "ticker"
    ORDERBOOK = "orderbook"
    TRADES = "trades"
    OHLCV = "ohlcv"
    USER_ORDERS = "user:orders"
    USER_TRADES = "user:trades"
    USER_BALANCES = "user:balances"


MessageHandler = Callable[[Dict[str, Any]], None]
AsyncMessageHandler = Callable[[Dict[str, Any]], Any]


class KlingExWebSocket:
    """WebSocket client for real-time KlingEx data"""

    DEFAULT_WS_URL = "wss://ws.klingex.io"

    def __init__(
        self,
        api_key: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.ws_url = ws_url or self.DEFAULT_WS_URL
        self._ws: Optional[WebSocketClientProtocol] = None
        self._subscriptions: Set[str] = set()
        self._handlers: Dict[str, List[AsyncMessageHandler]] = {}
        self._running = False
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 60.0

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
                if self._running:
                    await self._handle_reconnect()
            except Exception as e:
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
        channel = data.get("channel") or data.get("type")
        if not channel:
            return

        # Call channel-specific handlers
        if channel in self._handlers:
            for handler in self._handlers[channel]:
                try:
                    result = handler(data)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    pass  # Don't let handler errors break the loop

        # Call wildcard handlers
        if "*" in self._handlers:
            for handler in self._handlers["*"]:
                try:
                    result = handler(data)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    pass

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

    async def close(self) -> None:
        """Close WebSocket connection"""
        self._running = False
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def __aenter__(self) -> "KlingExWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
