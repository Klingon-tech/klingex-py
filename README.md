# KlingEx Python SDK

Official Python SDK for the KlingEx Exchange API.

## Installation

```bash
pip install klingex
```

Or install from source:

```bash
git clone https://github.com/Klingon-tech/klingex-py.git
cd klingex-py
pip install -e .
```

## Quick Start

### Public API (No Authentication Required)

```python
from klingex import KlingEx

# Create client (no credentials needed for public endpoints)
client = KlingEx()

# Get all available markets
markets = client.markets.get_markets()
for market in markets:
    print(f"{market.symbol}: {market.base_asset}/{market.quote_asset}")

# Get ticker for a specific market
ticker = client.markets.get_ticker("BTC-USDT")
print(f"BTC-USDT: {ticker.last_price} ({ticker.change_percent_24h}%)")

# Get orderbook
orderbook = client.markets.get_orderbook("BTC-USDT", depth=10)
print(f"Best bid: {orderbook.bids[0].price}")
print(f"Best ask: {orderbook.asks[0].price}")

# Get recent trades
trades = client.markets.get_trades("BTC-USDT", limit=50)
for trade in trades[:5]:
    print(f"{trade.side}: {trade.quantity} @ {trade.price}")

# Get OHLCV candlestick data
candles = client.markets.get_ohlcv("BTC-USDT", interval="1h", limit=24)
for candle in candles:
    print(f"{candle.timestamp}: O={candle.open} H={candle.high} L={candle.low} C={candle.close}")
```

### Authenticated API

```python
from klingex import KlingEx, OrderSide, OrderType

# Create client with API key
client = KlingEx(api_key="your_api_key")

# Get wallet balances
balances = client.wallet.get_balances()
for balance in balances:
    if float(balance.total) > 0:
        print(f"{balance.symbol}: {balance.available} available, {balance.locked} locked")

# Place a limit order (human-readable values by default)
order = client.orders.submit_order(
    market_id="BTC-USDT",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity="0.001",  # 0.001 BTC
    price="50000",     # $50,000 per BTC
)
print(f"Order placed: {order.order_id}")

# Place a market order
order = client.orders.submit_order(
    market_id="BTC-USDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity="0.001",
)

# Cancel an order
client.orders.cancel_order(order.order_id)

# Cancel all orders for a market
client.orders.cancel_all_orders(market_id="BTC-USDT")

# Get open orders
open_orders = client.orders.get_open_orders()
for order in open_orders:
    print(f"{order.id}: {order.side} {order.quantity} @ {order.price}")

# Get order history
history = client.orders.get_order_history(limit=10)
```

### Raw Values Mode

By default, quantity and price use human-readable values (e.g., "1.5" for 1.5 BTC). For raw base unit values (e.g., satoshis), use `raw_values=True`:

```python
# Human-readable (default)
order = client.orders.submit_order(
    market_id="BTC-USDT",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity="0.5",      # 0.5 BTC
    price="45000",       # $45,000
)

# Raw base units
order = client.orders.submit_order(
    market_id="BTC-USDT",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity="50000000", # 50,000,000 satoshis = 0.5 BTC
    price="4500000",     # $45,000 in cents
    raw_values=True,
)
```

### Async Client

```python
import asyncio
from klingex import AsyncKlingEx, OrderSide, OrderType

async def main():
    async with AsyncKlingEx(api_key="your_api_key") as client:
        # Fetch multiple resources concurrently
        markets, tickers, balances = await asyncio.gather(
            client.markets.get_markets(),
            client.markets.get_tickers(),
            client.wallet.get_balances(),
        )

        # Place order
        order = await client.orders.submit_order(
            market_id="BTC-USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity="0.001",
            price="50000",
        )

asyncio.run(main())
```

### WebSocket Streaming

```python
import asyncio
from klingex import KlingExWebSocket

async def main():
    ws = KlingExWebSocket(api_key="your_api_key")  # Optional, for private channels

    # Define handlers
    def on_ticker(data):
        ticker = data.get("data", {})
        print(f"Ticker: {ticker.get('lastPrice')}")

    def on_trade(data):
        trade = data.get("data", {})
        print(f"Trade: {trade.get('side')} {trade.get('quantity')} @ {trade.get('price')}")

    def on_order_update(data):
        order = data.get("data", {})
        print(f"Order: {order.get('id')} - {order.get('status')}")

    # Connect and subscribe
    await ws.connect()

    # Public channels
    await ws.subscribe_ticker("BTC-USDT", on_ticker)
    await ws.subscribe_trades("BTC-USDT", on_trade)
    await ws.subscribe_orderbook("BTC-USDT")

    # Private channels (requires auth)
    await ws.subscribe_user_orders(on_order_update)
    await ws.subscribe_user_trades()
    await ws.subscribe_user_balances()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await ws.close()

asyncio.run(main())
```

### Wallet Operations

```python
# Get deposit address
address = client.wallet.get_deposit_address("BTC")
print(f"Deposit to: {address.address}")

# For multi-chain assets
address = client.wallet.get_deposit_address("USDT", chain="erc20")

# Get deposit history
deposits = client.wallet.get_deposits(asset_id="BTC", limit=10)
for deposit in deposits:
    print(f"{deposit.amount} BTC - {deposit.status}")

# Request withdrawal
withdrawal = client.wallet.request_withdrawal(
    asset_id="BTC",
    amount="0.01",
    address="bc1q...",
    two_fa_code="123456",  # If 2FA enabled
)
print(f"Withdrawal ID: {withdrawal.id}")

# Get withdrawal history
withdrawals = client.wallet.get_withdrawals(status="completed")
```

### Invoice/Payment Processing

```python
# Create an invoice
invoice = client.invoices.create_invoice(
    asset_id="BTC",
    amount="0.001",
    description="Order #12345",
    callback_url="https://yoursite.com/webhook",
    redirect_url="https://yoursite.com/thank-you",
    expires_in_minutes=60,
)
print(f"Invoice ID: {invoice.id}")
print(f"Pay to: {invoice.payment_address}")

# Get invoice status
invoice = client.invoices.get_invoice(invoice.id)
print(f"Status: {invoice.status}")

# Get payments for invoice
payments = client.invoices.get_invoice_payments(invoice.id)
```

## Error Handling

```python
from klingex import (
    KlingEx,
    KlingExError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

client = KlingEx(api_key="your_api_key")

try:
    order = client.orders.submit_order(...)
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except KlingExError as e:
    print(f"API error: {e.message} (code: {e.code})")
```

## Configuration

```python
client = KlingEx(
    api_key="your_api_key",
    base_url="https://api.klingex.io",  # Custom API URL
    timeout=30.0,                        # Request timeout in seconds
)
```

## API Reference

### Client Classes

- `KlingEx` - Synchronous client
- `AsyncKlingEx` - Asynchronous client
- `KlingExWebSocket` - WebSocket client for real-time data

### Endpoint Modules

- `client.markets` - Public market data (assets, markets, tickers, orderbook, trades, OHLCV)
- `client.orders` - Order management (submit, cancel, list orders)
- `client.wallet` - Wallet operations (balances, deposits, withdrawals)
- `client.invoices` - Invoice/payment processing

### Types

- `OrderSide` - `BUY`, `SELL`
- `OrderType` - `LIMIT`, `MARKET`
- `OrderStatus` - `PENDING`, `OPEN`, `PARTIAL`, `FILLED`, `CANCELLED`
- `TimeInForce` - `GTC`, `IOC`, `FOK`

### Exceptions

- `KlingExError` - Base exception
- `AuthenticationError` - Invalid API credentials
- `RateLimitError` - Rate limit exceeded
- `ValidationError` - Invalid request parameters

## Examples

See the [examples](./examples) directory for complete working examples:

- `basic_trading.py` - Basic trading operations
- `async_trading.py` - Async/concurrent operations
- `websocket_stream.py` - Real-time data streaming
- `market_maker.py` - Simple market-making strategy

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Support

- Documentation: https://klingex.io/support/api-docs
- Issues: https://github.com/Klingon-tech/klingex-py/issues
- Email: support@klingex.io
