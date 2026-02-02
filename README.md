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
for market in markets[:5]:
    print(f"{market.symbol}: {market.base_asset_symbol}/{market.quote_asset_symbol}")

# Get tickers for all markets (CMC/CoinGecko format)
tickers = client.markets.get_tickers()
for ticker in tickers[:3]:
    print(f"{ticker.ticker_id}: {ticker.last_price}")

# Get ticker for a specific market (use underscore format)
ticker = client.markets.get_ticker("BTC_USDT")
print(f"BTC_USDT: {ticker.last_price} (bid: {ticker.bid}, ask: {ticker.ask})")

# Get orderbook (market_id is an integer)
orderbook = client.markets.get_orderbook(market_id=1)
print(f"Best bid: {orderbook.bids[0][0]} @ {orderbook.bids[0][1]}")
print(f"Best ask: {orderbook.asks[0][0]} @ {orderbook.asks[0][1]}")

# Get OHLCV candlestick data
candles = client.markets.get_ohlcv(market_id=1, timeframe="1h", limit=24)
for candle in candles[:3]:
    print(f"{candle.time_bucket}: O={candle.open_price} H={candle.high_price} L={candle.low_price} C={candle.close_price}")
```

### Authenticated API

```python
from klingex import KlingEx, OrderSide

# Create client with API key
client = KlingEx(api_key="your_api_key")

# Get wallet balances
balances = client.wallet.get_balances()
for balance in balances:
    if int(balance.balance) > 0:
        print(f"{balance.symbol}: {balance.available} available, {balance.locked_balance} locked")

# Get balance for a specific asset
btc_balance = client.wallet.get_balance("BTC")
print(f"BTC: {btc_balance.balance}")

# Place a limit order (human-readable values by default)
order = client.orders.submit_order(
    symbol="BTC-USDT",
    trading_pair_id=1,
    side=OrderSide.BUY,
    quantity="0.001",  # 0.001 BTC
    price="50000",     # $50,000 per BTC
)
print(f"Order placed: {order.order_id}")

# Place a market order (price="0")
market_order = client.orders.submit_order(
    symbol="BTC-USDT",
    trading_pair_id=1,
    side=OrderSide.BUY,
    quantity="0.001",
    price="0",          # Price 0 = market order
    slippage=0.01,      # 1% slippage tolerance
)

# Cancel an order (requires both order_id and trading_pair_id)
result = client.orders.cancel_order(order.order_id, trading_pair_id=1)
print(f"Cancelled: {result.message}, released: {result.released_balance}")

# Get open orders
open_orders = client.orders.get_open_orders()
for order in open_orders:
    print(f"{order.id}: {order.side} {order.amount} @ {order.price}")

# Get all orders (with optional filters)
orders = client.orders.get_orders(trading_pair_id=1, status="pending", limit=50)
```

### Raw Values Mode

By default, quantity and price use human-readable values (e.g., "1.5" for 1.5 BTC). For raw base unit values (e.g., satoshis), use `raw_values=True`:

```python
# Human-readable (default)
order = client.orders.submit_order(
    symbol="BTC-USDT",
    trading_pair_id=1,
    side=OrderSide.BUY,
    quantity="0.5",      # 0.5 BTC
    price="45000",       # $45,000
)

# Raw base units
order = client.orders.submit_order(
    symbol="BTC-USDT",
    trading_pair_id=1,
    side=OrderSide.BUY,
    quantity="50000000", # 50,000,000 satoshis = 0.5 BTC
    price="4500000",     # $45,000 in base units
    raw_values=True,
)
```

### Async Client

```python
import asyncio
from klingex import AsyncKlingEx, OrderSide

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
            symbol="BTC-USDT",
            trading_pair_id=1,
            side=OrderSide.BUY,
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

### Invoice/Payment Processing

```python
# Create an invoice
invoice = client.invoices.create_invoice(
    currency="USDT",
    amount="100.00",
    accepted_coins=["BTC", "ETH", "USDT"],
    description="Order #12345",
    expires_in_minutes=60,
)
print(f"Invoice ID: {invoice.id}")
print(f"Payment URL: {invoice.payment_page_url}")

# List invoices
invoice_list = client.invoices.list_invoices(status="pending", page=1, page_size=20)
for inv in invoice_list.invoices:
    print(f"{inv.id}: {inv.status}")

# Get invoice details
invoice = client.invoices.get_invoice(invoice.id)
print(f"Status: {invoice.status}")

# Cancel a pending invoice
client.invoices.cancel_invoice(invoice.id)

# Get fee statistics
fees = client.invoices.get_fee_stats()
print(f"Fee rate: {fees.current_fee_rate_percent}%")
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
    order = client.orders.submit_order(
        symbol="BTC-USDT",
        trading_pair_id=1,
        side="BUY",
        quantity="0.001",
        price="50000",
    )
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

- `client.markets` - Public market data (assets, markets, tickers, orderbook, OHLCV)
- `client.orders` - Order management (submit, cancel, list orders)
- `client.wallet` - Wallet operations (balances)
- `client.invoices` - Invoice/payment processing

### Types

- `OrderSide` - `BUY`, `SELL`
- `OrderType` - `LIMIT`, `MARKET`
- `OrderStatus` - `PENDING`, `OPEN`, `PARTIAL`, `FILLED`, `CANCELLED`

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
