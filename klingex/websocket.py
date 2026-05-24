"""KlingEx WebSocket Client.

Implements the exchange WebSocket protocol. Messages are sent as JSON
objects with the following envelope (only the fields used per action are
populated):

    {
        "action": "subscribe" | "unsubscribe" | "subscribe_ohlcv" | ...
                  | "ping" | "place_order" | "cancel_order",
        "type":   "<user-channel-type>" | "auth",
        "market": "BTC-USDT" | "markets" | ...,
        "market_id": int,           # for OHLCV
        "timeframe": "5m" | ...,    # for OHLCV
        "invoice_id": "<uuid>",     # for invoice subscriptions
        "session_token": "...",     # for QR login subscriptions
        "apiKey": "...",            # for API-key auth (note camelCase)
        "symbol": "BTC-USDT",       # order placement
        "tradingPairId": int,       # order placement / cancel
        "side": "buy" | "sell",     # order placement
        "quantity": "...",          # order placement
        "price": "...",             # order placement
        "rawValues": bool,          # order placement
        "orderId": "<uuid>",        # order cancel
        "requestId": "<uuid>"       # correlation id for order ops
    }

Public market data is subscribed via ``{"action": "subscribe",
"market": "<pair>"}`` (the server registers the client for the
``ticker``, ``orderbook`` and ``trades`` streams of that pair under a
single market subscription). User-private channels use
``{"action": "subscribe", "type": "<channel>"}`` where ``<channel>`` is
one of: ``balance`` (singular), ``orders``, ``transfer``, ``deposits``,
``withdrawals``, ``notifications``, ``trades``, ``account``.

API-key authentication is a post-connect message of the form
``{"type": "auth", "apiKey": "<key>"}``. The server replies with
``{"type": "auth_result", "success": true, ...}`` or
``{"type": "auth_result", "success": false, "error": "..."}``. Callers
must wait for ``auth_result`` before subscribing to user channels.

JWT auth via ``?token=...`` query parameter is also supported by the
backend (the server picks it up at handshake), but this SDK uses the
API-key path which is the standard for programmatic clients.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple, Union

import websockets

from klingex.http import AuthenticationError, KlingExError

# websockets>=14 removed ``WebSocketClientProtocol``; the connection object
# returned by ``connect()`` is just an opaque async iterable / sender.
WebSocketClientProtocol = Any  # type: ignore


MessageHandler = Callable[[Dict[str, Any]], Any]
"""Handler signature for incoming WebSocket messages.

Handlers may be plain callables or coroutine functions. Exceptions raised
inside a handler are caught and logged so they do not break the receive
loop.
"""


# User-channel names accepted by the server side.
VALID_USER_CHANNELS: Set[str] = {
    "balance",
    "orders",
    "transfer",
    "deposits",
    "withdrawals",
    "notifications",
    "trades",
    "account",
}


# Server `type` field -> SDK-side user-channel name. Unknown user-typed
# events (those with `user_id` but no entry here) are dropped — extend
# this table when a new exchange event type ships.
_USER_TYPE_TO_CHANNEL: Dict[str, str] = {
    # balance
    "balance_update": "balance",
    "balance_updated": "balance",
    # orders
    "order_created": "orders",
    "order_updated": "orders",
    "order_placed": "orders",
    "order_partial": "orders",
    "order_filled": "orders",
    "order_cancelled": "orders",
    "order_rejected": "orders",
    # transfer
    "transfer_updated": "transfer",
    # deposits
    "deposit_created": "deposits",
    "deposit_confirming": "deposits",
    "deposit_completed": "deposits",
    "deposit_rejected": "deposits",
    "deposit_updated": "deposits",
    # withdrawals
    "withdrawal_pending": "withdrawals",
    "withdrawal_processing": "withdrawals",
    "withdrawal_completed": "withdrawals",
    "withdrawal_failed": "withdrawals",
    "withdrawal_updated": "withdrawals",
    # user trades
    "user_trade": "trades",
    "trade_filled": "trades",
    # notifications + account
    "new_notification": "notifications",
    "account_event": "account",
}


# Public market event types broadcast over a market subscription.
_PUBLIC_MARKET_TYPES: Set[str] = {
    "ticker_update",
    "orderbook_snapshot",
    "trade_update",
}


def _market_key(market: str) -> str:
    return f"market:{market}"


def _user_key(channel: str) -> str:
    return f"user:{channel}"


def _ohlcv_key(market_id: int, timeframe: str) -> str:
    return f"ohlcv:{market_id}:{timeframe}"


def _invoice_key(invoice_id: str) -> str:
    return f"invoice:{invoice_id}"


def _qr_key(session_token: str) -> str:
    return f"qr:{session_token}"


class KlingExWebSocket:
    """Async WebSocket client for KlingEx real-time data and trading.

    Typical usage::

        async with KlingExWebSocket(api_key="...") as ws:
            await ws.subscribe_market("BTC-USDT", handler=on_market_event)
            await ws.subscribe_user("balance", handler=on_balance_event)
            ...

    Or, manually::

        ws = KlingExWebSocket(api_key="...")
        await ws.connect()
        await ws.subscribe_market("BTC-USDT", handler=on_event)
        ...
        await ws.close()

    When an API key is supplied the client will automatically authenticate
    after connecting and wait for ``auth_result`` before re-subscribing to
    any user channels recorded in the subscription set. If
    authentication fails the connection is closed and an
    :class:`AuthenticationError` is raised from :meth:`connect`.
    """

    DEFAULT_WS_URL = "wss://ws.klingex.io/ws"
    AUTH_TIMEOUT = 10.0
    REQUEST_TIMEOUT = 10.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        ws_url: Optional[str] = None,
        auto_reconnect: bool = True,
        on_message: Optional[MessageHandler] = None,
        on_error: Optional[MessageHandler] = None,
    ):
        self.api_key = api_key
        self.ws_url = ws_url or self.DEFAULT_WS_URL
        self.auto_reconnect = auto_reconnect

        # Subscription bookkeeping. We keep a deterministic record of every
        # subscription so we can replay it after a reconnect. Handlers are
        # stored per internal key (see _market_key / _user_key / etc.).
        # ``_market_subs`` etc. hold the parameters needed to re-send the
        # subscribe message.
        self._market_subs: Set[str] = set()
        self._user_subs: Set[str] = set()
        self._ohlcv_subs: Set[Tuple[int, str]] = set()
        self._invoice_subs: Set[str] = set()
        self._qr_subs: Set[str] = set()

        # ``_handlers[key]`` -> list of message handlers for that channel
        self._handlers: Dict[str, List[MessageHandler]] = {}

        # Global handlers
        self._on_message = on_message
        self._on_error = on_error

        # Internal state
        self._ws: Optional[WebSocketClientProtocol] = None
        self._running = False
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 60.0
        self._authenticated = False
        self._auth_future: Optional[asyncio.Future] = None
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._connect_task: Optional[asyncio.Task] = None
        self._ready_event = asyncio.Event()

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    async def connect(self) -> None:
        """Open the WebSocket connection and (if an API key is set) auth.

        Blocks until the connection is established and, when applicable,
        the server has acknowledged the authentication request. Raises
        :class:`AuthenticationError` if auth is rejected and
        :class:`KlingExError` on transport failures.
        """
        if self._running:
            return
        self._running = True

        try:
            await self._open_once()
        except Exception:
            self._running = False
            raise

        # Spawn the background message loop and reconnector
        loop = asyncio.get_event_loop()
        self._connect_task = loop.create_task(self._supervisor_loop())

    async def _open_once(self) -> None:
        """Open one WebSocket and run the auth handshake."""
        self._ws = await websockets.connect(self.ws_url)
        self._reconnect_delay = 1.0
        self._authenticated = False
        self._ready_event.clear()

        if self.api_key:
            await self._authenticate_and_wait()
        else:
            self._ready_event.set()

        # Replay subscriptions for reconnect scenarios
        await self._replay_subscriptions()

    async def _authenticate_and_wait(self) -> None:
        """Send the auth message and wait for ``auth_result``."""
        assert self._ws is not None
        loop = asyncio.get_event_loop()
        self._auth_future = loop.create_future()

        await self._ws.send(json.dumps({"type": "auth", "apiKey": self.api_key}))

        # Pump messages until auth_result arrives. We can't just await the
        # future without reading the socket because nothing else is
        # consuming bytes yet.
        try:
            await asyncio.wait_for(
                self._pump_until_auth(),
                timeout=self.AUTH_TIMEOUT,
            )
        except asyncio.TimeoutError as exc:
            await self._safe_close_ws()
            raise AuthenticationError(
                "Timed out waiting for WebSocket auth_result"
            ) from exc

        assert self._auth_future is not None
        if not self._authenticated:
            err = self._auth_future.result() if self._auth_future.done() else None
            await self._safe_close_ws()
            raise AuthenticationError(
                str(err) if err else "WebSocket authentication failed"
            )
        self._ready_event.set()

    async def _pump_until_auth(self) -> None:
        """Read messages until auth_result is observed."""
        assert self._ws is not None
        async for raw in self._ws:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            await self._handle_message(data)
            if self._authenticated or (
                self._auth_future is not None and self._auth_future.done()
            ):
                return

    async def _replay_subscriptions(self) -> None:
        assert self._ws is not None
        for market in list(self._market_subs):
            await self._send({"action": "subscribe", "market": market})
        if self._authenticated:
            for channel in list(self._user_subs):
                await self._send({"action": "subscribe", "type": channel})
        for market_id, timeframe in list(self._ohlcv_subs):
            await self._send({
                "action": "subscribe_ohlcv",
                "market_id": market_id,
                "timeframe": timeframe,
            })
        for invoice_id in list(self._invoice_subs):
            await self._send({"action": "subscribe_invoice", "invoice_id": invoice_id})
        for session_token in list(self._qr_subs):
            await self._send({"action": "subscribe_qr", "session_token": session_token})

    async def _supervisor_loop(self) -> None:
        """Background loop that reads messages and reconnects on failure."""
        try:
            await self._message_loop()
        finally:
            while self._running and self.auto_reconnect:
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(
                    self._reconnect_delay * 2,
                    self._max_reconnect_delay,
                )
                try:
                    await self._open_once()
                    await self._message_loop()
                except Exception as exc:
                    if self._on_error is not None:
                        await self._dispatch_handler(
                            self._on_error,
                            {"type": "error", "error": str(exc)},
                        )
                    continue

    async def _message_loop(self) -> None:
        ws = self._ws
        if ws is None:
            return
        try:
            async for raw in ws:
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                await self._handle_message(data)
        except websockets.ConnectionClosed:
            self._reject_pending_requests("Connection closed")
        finally:
            self._ws = None

    # ------------------------------------------------------------------
    # Message dispatch
    # ------------------------------------------------------------------
    async def _handle_message(self, data: Dict[str, Any]) -> None:
        msg_type = data.get("type")

        # Global handler always sees the message first
        if self._on_message is not None:
            await self._dispatch_handler(self._on_message, data)

        # Auth handshake
        if msg_type == "auth_result":
            success = bool(data.get("success"))
            self._authenticated = success
            if self._auth_future is not None and not self._auth_future.done():
                self._auth_future.set_result(
                    None if success else data.get("error", "Authentication failed")
                )
            return

        # Order placement / cancellation correlation by requestId
        if msg_type in ("order_result", "cancel_result"):
            request_id = data.get("requestId")
            if request_id and request_id in self._pending_requests:
                fut = self._pending_requests.pop(request_id)
                if not fut.done():
                    fut.set_result(data)
            await self._dispatch_to_channel(msg_type, data)
            return

        # Error envelope
        if msg_type == "error" and self._on_error is not None:
            await self._dispatch_handler(self._on_error, data)

        # Discriminate user vs public on ``user_id``: private order/trade
        # frames carry both ``user_id`` AND ``market``, so we can't infer
        # "this is a market event" from the presence of ``market`` alone.
        user_id = data.get("user_id")
        user_channel = _USER_TYPE_TO_CHANNEL.get(msg_type) if msg_type else None
        is_user_event = bool(user_id) or user_channel is not None

        if is_user_event:
            if user_channel is not None:
                await self._dispatch_to_channel(_user_key(user_channel), data)
            # Unknown user-typed event (or one we can't classify yet):
            # drop silently. The server-side `client_count` heartbeat has
            # no ``user_id``, so it won't get here.
            return

        # Public market events carry a ``market`` field.
        market = data.get("market")
        if market:
            await self._dispatch_to_channel(_market_key(market), data)

        # OHLCV frames carry market_id + timeframe.
        if msg_type == "ohlcv" or msg_type == "ohlcv_update":
            market_id = data.get("market_id") or data.get("trading_pair_id")
            timeframe = data.get("timeframe")
            if market_id and timeframe:
                await self._dispatch_to_channel(_ohlcv_key(int(market_id), timeframe), data)

        # Invoice frames
        if msg_type and msg_type.startswith("invoice"):
            invoice_id = data.get("invoice_id") or data.get("id")
            if invoice_id:
                await self._dispatch_to_channel(_invoice_key(invoice_id), data)

        # QR login frames
        if msg_type and msg_type.startswith("qr"):
            session_token = data.get("session_token")
            if session_token:
                await self._dispatch_to_channel(_qr_key(session_token), data)

    async def _dispatch_to_channel(self, key: str, data: Dict[str, Any]) -> None:
        handlers = self._handlers.get(key)
        if not handlers:
            return
        for handler in list(handlers):
            await self._dispatch_handler(handler, data)

    async def _dispatch_handler(
        self, handler: MessageHandler, data: Dict[str, Any]
    ) -> None:
        try:
            result = handler(data)
            if asyncio.iscoroutine(result):
                await result
        except Exception as exc:
            # Don't let handler errors break the loop; surface via on_error
            if self._on_error is not None and handler is not self._on_error:
                try:
                    err_payload = {
                        "type": "handler_error",
                        "error": str(exc),
                    }
                    result = self._on_error(err_payload)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Low-level send helpers
    # ------------------------------------------------------------------
    async def _send(self, payload: Dict[str, Any]) -> None:
        if self._ws is None:
            raise KlingExError("WebSocket is not connected")
        await self._ws.send(json.dumps(payload))

    async def _safe_close_ws(self) -> None:
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    def _reject_pending_requests(self, reason: str) -> None:
        for request_id, fut in list(self._pending_requests.items()):
            if not fut.done():
                fut.set_exception(KlingExError(reason))
        self._pending_requests.clear()

    async def _wait_ready(self) -> None:
        await self._ready_event.wait()

    # ------------------------------------------------------------------
    # Public subscription API
    # ------------------------------------------------------------------
    async def subscribe_market(
        self,
        market: str,
        handler: Optional[MessageHandler] = None,
    ) -> None:
        """Subscribe to public market data (ticker, orderbook, trades).

        Args:
            market: Trading pair symbol like ``"BTC-USDT"``. The special
                string ``"markets"`` subscribes to the markets-list feed.
            handler: Optional handler receiving every event for this
                market.
        """
        await self._wait_ready()
        self._market_subs.add(market)
        if handler is not None:
            self._handlers.setdefault(_market_key(market), []).append(handler)
        await self._send({"action": "subscribe", "market": market})

    async def unsubscribe_market(self, market: str) -> None:
        self._market_subs.discard(market)
        self._handlers.pop(_market_key(market), None)
        if self._ws is not None:
            await self._send({"action": "unsubscribe", "market": market})

    async def subscribe_user(
        self,
        channel: str,
        handler: Optional[MessageHandler] = None,
    ) -> None:
        """Subscribe to a user-private channel (requires authentication).

        Valid channels: ``balance`` (singular), ``orders``, ``transfer``,
        ``deposits``, ``withdrawals``, ``notifications``, ``trades``,
        ``account``.
        """
        if channel not in VALID_USER_CHANNELS:
            raise ValueError(
                f"Invalid user channel '{channel}'. Valid: {sorted(VALID_USER_CHANNELS)}"
            )
        if not self.api_key and not self._authenticated:
            raise AuthenticationError(
                "User channel subscriptions require an authenticated session "
                "(pass api_key=... when constructing KlingExWebSocket)"
            )
        await self._wait_ready()
        if not self._authenticated:
            raise AuthenticationError("WebSocket is not authenticated")
        self._user_subs.add(channel)
        if handler is not None:
            self._handlers.setdefault(_user_key(channel), []).append(handler)
        await self._send({"action": "subscribe", "type": channel})

    async def unsubscribe_user(self, channel: str) -> None:
        self._user_subs.discard(channel)
        self._handlers.pop(_user_key(channel), None)
        if self._ws is not None:
            await self._send({"action": "unsubscribe", "type": channel})

    async def subscribe_ohlcv(
        self,
        market_id: int,
        timeframe: str,
        handler: Optional[MessageHandler] = None,
    ) -> None:
        """Subscribe to OHLCV (candlestick) updates for a market."""
        await self._wait_ready()
        self._ohlcv_subs.add((market_id, timeframe))
        if handler is not None:
            self._handlers.setdefault(_ohlcv_key(market_id, timeframe), []).append(handler)
        await self._send({
            "action": "subscribe_ohlcv",
            "market_id": market_id,
            "timeframe": timeframe,
        })

    async def unsubscribe_ohlcv(self, market_id: int, timeframe: str) -> None:
        self._ohlcv_subs.discard((market_id, timeframe))
        self._handlers.pop(_ohlcv_key(market_id, timeframe), None)
        if self._ws is not None:
            await self._send({
                "action": "unsubscribe_ohlcv",
                "market_id": market_id,
                "timeframe": timeframe,
            })

    async def subscribe_invoice(
        self,
        invoice_id: str,
        handler: Optional[MessageHandler] = None,
    ) -> None:
        """Subscribe to invoice payment updates."""
        await self._wait_ready()
        self._invoice_subs.add(invoice_id)
        if handler is not None:
            self._handlers.setdefault(_invoice_key(invoice_id), []).append(handler)
        await self._send({"action": "subscribe_invoice", "invoice_id": invoice_id})

    async def unsubscribe_invoice(self, invoice_id: str) -> None:
        self._invoice_subs.discard(invoice_id)
        self._handlers.pop(_invoice_key(invoice_id), None)
        if self._ws is not None:
            await self._send({"action": "unsubscribe_invoice", "invoice_id": invoice_id})

    async def subscribe_qr(
        self,
        session_token: str,
        handler: Optional[MessageHandler] = None,
    ) -> None:
        """Subscribe to QR-login session updates."""
        await self._wait_ready()
        self._qr_subs.add(session_token)
        if handler is not None:
            self._handlers.setdefault(_qr_key(session_token), []).append(handler)
        await self._send({"action": "subscribe_qr", "session_token": session_token})

    async def unsubscribe_qr(self, session_token: str) -> None:
        self._qr_subs.discard(session_token)
        self._handlers.pop(_qr_key(session_token), None)
        if self._ws is not None:
            await self._send({"action": "unsubscribe_qr", "session_token": session_token})

    # ------------------------------------------------------------------
    # Backwards-compatible aliases (older SDK API)
    # ------------------------------------------------------------------
    async def subscribe_ticker(
        self, market: Union[str, int], handler: Optional[MessageHandler] = None
    ) -> None:
        """Backwards-compatible alias for :meth:`subscribe_market`.

        The backend exposes a single subscription per market that
        delivers ticker + orderbook + trade frames; subscribing to the
        ticker alone is not a separate operation.
        """
        await self.subscribe_market(str(market), handler)

    async def subscribe_orderbook(
        self, market: Union[str, int], handler: Optional[MessageHandler] = None
    ) -> None:
        """Backwards-compatible alias for :meth:`subscribe_market`."""
        await self.subscribe_market(str(market), handler)

    async def subscribe_trades(
        self, market: Union[str, int], handler: Optional[MessageHandler] = None
    ) -> None:
        """Backwards-compatible alias for :meth:`subscribe_market`."""
        await self.subscribe_market(str(market), handler)

    async def subscribe_user_orders(self, handler: Optional[MessageHandler] = None) -> None:
        await self.subscribe_user("orders", handler)

    async def subscribe_user_trades(self, handler: Optional[MessageHandler] = None) -> None:
        await self.subscribe_user("trades", handler)

    async def subscribe_user_balances(self, handler: Optional[MessageHandler] = None) -> None:
        """Alias for ``subscribe_user("balance")`` (note: backend channel is singular)."""
        await self.subscribe_user("balance", handler)

    async def subscribe_account(self, handler: Optional[MessageHandler] = None) -> None:
        await self.subscribe_user("account", handler)

    # ------------------------------------------------------------------
    # Ping
    # ------------------------------------------------------------------
    async def ping(self) -> None:
        """Send an application-level ping. The server replies with pong."""
        await self._wait_ready()
        await self._send({"action": "ping"})

    # ------------------------------------------------------------------
    # Trading methods
    # ------------------------------------------------------------------
    async def place_order(
        self,
        symbol: str,
        trading_pair_id: int,
        side: str,
        quantity: str,
        price: str,
        raw_values: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place an order via the WebSocket.

        The backend proxies the request to the HTTP API and returns an
        ``order_result`` message correlated by ``requestId``.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC-USDT"``).
            trading_pair_id: Trading pair ID.
            side: ``"buy"`` or ``"sell"`` (case-insensitive).
            quantity: Order quantity (string to preserve precision).
            price: Order price (``"0"`` for market orders).
            raw_values: When ``True`` quantity/price are interpreted as
                base units (smallest indivisible unit).
        """
        return await self._send_request(
            "place_order",
            {
                "symbol": symbol,
                "tradingPairId": trading_pair_id,
                "side": side,
                "quantity": quantity,
                "price": price,
                "rawValues": raw_values,
            },
            timeout=timeout,
            success_error_msg="Order failed",
        )

    async def cancel_order(
        self,
        order_id: str,
        trading_pair_id: int,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Cancel an order via the WebSocket."""
        return await self._send_request(
            "cancel_order",
            {
                "orderId": order_id,
                "tradingPairId": trading_pair_id,
            },
            timeout=timeout,
            success_error_msg="Cancel failed",
        )

    async def _send_request(
        self,
        action: str,
        payload: Dict[str, Any],
        timeout: Optional[float],
        success_error_msg: str,
    ) -> Dict[str, Any]:
        await self._wait_ready()
        request_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self._pending_requests[request_id] = future

        await self._send({**payload, "action": action, "requestId": request_id})
        try:
            result = await asyncio.wait_for(
                future, timeout if timeout is not None else self.REQUEST_TIMEOUT
            )
        finally:
            self._pending_requests.pop(request_id, None)

        if not result.get("success", True):
            raise KlingExError(result.get("error", success_error_msg))
        return result

    # ------------------------------------------------------------------
    # Handler registration helpers (used after subscribe)
    # ------------------------------------------------------------------
    def on_market(self, market: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(_market_key(market), []).append(handler)

    def on_user(self, channel: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(_user_key(channel), []).append(handler)

    def on_ohlcv(self, market_id: int, timeframe: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(_ohlcv_key(market_id, timeframe), []).append(handler)

    def on_invoice(self, invoice_id: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(_invoice_key(invoice_id), []).append(handler)

    def on_qr(self, session_token: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(_qr_key(session_token), []).append(handler)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    async def close(self) -> None:
        """Close the WebSocket connection and stop the supervisor loop."""
        self._running = False
        self._reject_pending_requests("Connection closed by client")
        await self._safe_close_ws()
        if self._connect_task is not None:
            self._connect_task.cancel()
            try:
                await self._connect_task
            except (asyncio.CancelledError, Exception):
                pass
            self._connect_task = None

    async def __aenter__(self) -> "KlingExWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
