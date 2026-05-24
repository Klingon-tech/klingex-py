# KlingEx Python SDK

Official Python SDK for the [KlingEx](https://klingex.io) cryptocurrency exchange API.

## Installation

```bash
pip install klingex
```

From source:

```bash
git clone https://github.com/Klingon-tech/klingex-py.git
cd klingex-py
pip install -e .
```

## Authentication

The SDK authenticates **with API keys only** (`X-API-Key` header). JWT-only
backend routes (account/profile/2FA management, deposit-address generation,
deposit/withdrawal history, etc.) are intentionally not exposed.

Generate a key in the web UI, granting only the scopes you need:

| Scope       | What it unlocks                                                 |
|-------------|-----------------------------------------------------------------|
| `read`      | Balances, orders/trade history, LP positions, mining-pool data  |
| `trade`     | Submit / cancel orders, cancel-all, create gift codes           |
| `withdraw`  | Submit on-chain withdrawals                                     |
| `liquidity` | Add / remove liquidity from AMM pools                           |

Granting `withdraw` requires 2FA at key-creation time; submission then skips
interactive 2FA so the key can be used unattended.

## Quick start

### Public market data (no auth)

```python
from klingex import KlingEx

client = KlingEx()

markets = client.markets.get_markets()
for market in markets[:5]:
    print(f"{market.base_asset_symbol}-{market.quote_asset_symbol}: {market.last_price}")

# CMC/CoinGecko-style tickers use the underscore form
ticker = client.markets.get_ticker("BTC_USDT")
print(f"BTC_USDT bid={ticker.bid} ask={ticker.ask}")

# Orderbook is keyed by trading_pair_id
ob = client.markets.get_orderbook(market_id=1)
print(f"Best bid: {ob.bids[0][0]} @ {ob.bids[0][1]}")

# Sparklines / per-pair info
sparks = client.markets.get_sparklines()
info = client.markets.get_market_info(base_symbol="BTC", quote_symbol="USDT")
asset = client.markets.get_asset_info("BTC")
```

### Authenticated REST

```python
from klingex import KlingEx, OrderSide

client = KlingEx(api_key="your_api_key")

# Balances (requires `read` scope)
for b in client.wallet.get_balances():
    if int(b.balance) > 0:
        print(f"{b.symbol}: available={b.available} locked={b.locked_balance}")

# Submit a limit order (`trade` scope). Human-readable amounts by default.
order = client.orders.submit_order(
    symbol="BTC-USDT",
    trading_pair_id=1,
    side=OrderSide.BUY,
    quantity="0.001",
    price="50000",
)

# Market order: pass price="0"
client.orders.submit_order(
    symbol="BTC-USDT", trading_pair_id=1, side=OrderSide.BUY,
    quantity="0.001", price="0",
)

# Cancel one / cancel all
client.orders.cancel_order(order.order_id, trading_pair_id=1)
client.orders.cancel_all_orders(trading_pair_id=1)

# Order history with filters (requires `read` scope)
history = client.orders.get_orders_history(
    trading_pair_id=1, status="filled", limit=50,
)
```

### Withdrawals

```python
# Amount is RAW INTEGER BASE UNITS (no decimal point).
# Example: 0.1 BTC has 8 decimals -> 10_000_000 satoshis.
result = client.withdrawals.submit(
    symbol="BTC",
    asset_id=1,
    amount="10000000",
    address="bc1q...",
)
print(result.withdrawal_id)

# XRP destination tag / Graphene memo are first-class:
client.withdrawals.submit(
    symbol="XRP", asset_id=42, amount="1000000",
    address="rXyz...", destination_tag=12345,
)
```

### Liquidity pools

```python
# Public reads (no auth)
pools = client.pools.list()
detail = client.pools.get(pool_id=1)

# `read` scope
positions = client.pools.positions()
chart = client.pools.position_history(pool_id=1, days=30)

# `liquidity` scope. Amounts are smallest base units.
mint = client.pools.add_liquidity(
    pool_id=1,
    base_amount_max="100000000",      # max base to deposit
    quote_amount_max="5000000000",    # max quote to deposit
    min_lp_tokens="1",                # slippage protection
)
burn = client.pools.remove_liquidity(
    pool_id=1,
    lp_tokens=mint.lp_tokens_minted,
    min_base_out="0",
    min_quote_out="0",
)
```

### Mining pool

```python
configs = client.mining_pool.get_configs()
stats = client.mining_pool.get_stats(symbol="HTN")
top = client.mining_pool.get_leaderboard(symbol="HTN")

# `read` scope
workers = client.mining_pool.get_my_workers()
rewards = client.mining_pool.get_my_rewards()
payouts = client.mining_pool.get_my_payouts()
```

### Gift codes (`trade` scope)

```python
single = client.gift_codes.create(asset_id=1, amount="100000000")  # 1 USDT
print(single.codes[0].code)

batch = client.gift_codes.create_bulk(asset_id=1, amount_per_code="10000000", count=20)
```

### Invoices

```python
# Amount in invoice creation is HUMAN-READABLE (e.g., "100.00" for 100 USDT).
invoice = client.invoices.create_invoice(
    currency="USDT",
    amount="100.00",
    accepted_coins=["BTC", "ETH", "USDT"],
    description="Order #12345",
    expires_in_minutes=60,
)
print(invoice.payment_page_url)

# Each payment option in `invoice.payment_options` is what the buyer pays with;
# the buyer picks one and sends `expected_amount` to `address`.
for opt in invoice.payment_options or []:
    print(f"{opt.symbol}: send {opt.expected_amount} to {opt.address}")

# List / cancel / fee stats
invoice_list = client.invoices.list_invoices(status="pending", page=1, page_size=20)
client.invoices.cancel_invoice(invoice.id)
fees = client.invoices.get_fee_stats()
```

### Async client

```python
import asyncio
from klingex import AsyncKlingEx, OrderSide

async def main():
    async with AsyncKlingEx(api_key="your_api_key") as client:
        markets, balances = await asyncio.gather(
            client.markets.get_markets(),
            client.wallet.get_balances(),
        )
        await client.orders.submit_order(
            symbol="BTC-USDT", trading_pair_id=1, side=OrderSide.BUY,
            quantity="0.001", price="50000",
        )

asyncio.run(main())
```

## WebSocket

The WebSocket client speaks the real wire protocol: one subscription per
trading pair delivers ticker + orderbook + trades, and user channels use
bare names (`balance` singular, `orders`, `trades`, `account`, ...).
API-key auth is performed post-connect; `connect()` blocks until the server
replies with `auth_result`.

```python
import asyncio
from klingex import KlingExWebSocket

async def main():
    ws = KlingExWebSocket(api_key="your_api_key")  # omit for public-only

    def on_market(msg):
        # msg["type"] is one of "ticker", "orderbook", "trade" (and friends)
        print(msg.get("type"), msg.get("market"))

    def on_orders(msg):
        print("order update", msg)

    def on_balance(msg):
        print("balance update", msg)

    await ws.connect()  # waits for auth_result if api_key was provided

    # Public — one subscription per market covers ticker+orderbook+trades.
    await ws.subscribe_market("BTC-USDT", on_market)
    await ws.subscribe_ohlcv(market_id=1, timeframe="5m", handler=lambda d: print(d))

    # User channels (require `read` scope)
    await ws.subscribe_user("orders", on_orders)
    await ws.subscribe_user("balance", on_balance)   # NOTE: singular "balance"

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await ws.close()

asyncio.run(main())
```

### WebSocket trading

```python
result = await ws.place_order(
    symbol="BTC-USDT", trading_pair_id=1, side="BUY",
    quantity="0.001", price="50000",
)
print(result["orderId"])

await ws.cancel_order(order_id=result["orderId"], trading_pair_id=1)
```

## Amount units cheat-sheet

| Where                              | Units                                          |
|------------------------------------|------------------------------------------------|
| `orders.submit_order` (default)    | Human-readable (`"1.5"` for 1.5 BTC)           |
| `orders.submit_order(raw_values=True)` | Smallest base units (`"150000000"`)        |
| `withdrawals.submit`               | **Raw integer base units only** (no decimals)  |
| `pools.add_liquidity` / `remove_liquidity` | Smallest base units                    |
| `invoices.create_invoice`          | Human-readable for the chosen denomination     |
| `gift_codes.create` / `create_bulk` | Smallest base units                           |

## Error handling

```python
from klingex import KlingExError, AuthenticationError, RateLimitError, ValidationError

try:
    client.orders.submit_order(...)
except AuthenticationError as e:
    print(f"Bad key or missing scope: {e.message}")
except RateLimitError as e:
    print(f"Retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Bad request: {e.message}")
except KlingExError as e:
    print(f"{e.status_code}: {e.message}")
```

## Configuration

```python
client = KlingEx(
    api_key="your_api_key",
    base_url="https://api.klingex.io",
    timeout=30.0,
)
```

## API reference

### Client classes

- `KlingEx` — synchronous client
- `AsyncKlingEx` — async client
- `KlingExWebSocket` — async WebSocket client

### Endpoint modules

| `client.markets`     | Public market data (assets, markets, tickers, orderbook, OHLCV, sparklines, asset-info, market-info) |
| `client.orders`      | Submit / cancel / cancel-all / list / history                                                        |
| `client.wallet`      | Balances + public wallet/sync status                                                                 |
| `client.withdrawals` | On-chain withdrawal submission (`withdraw` scope)                                                    |
| `client.pools`       | AMM pool data, LP positions, add/remove liquidity                                                    |
| `client.invoices`    | Merchant invoice create / list / get / cancel / fee stats / PDF                                      |
| `client.mining_pool` | Public pool stats + authed worker/rewards/payouts                                                    |
| `client.gift_codes`  | Single + bulk gift-code creation                                                                     |

### Enums

- `OrderSide` — `BUY`, `SELL` (string values `"buy"` / `"sell"`)
- `OrderType` — `LIMIT`, `MARKET`
- `OrderStatus` — `PENDING`, `PARTIAL`, `FILLED`, `CANCELLED`, `REJECTED`

### Exceptions

`KlingExError` (base), `AuthenticationError`, `RateLimitError`, `ValidationError`.

## Examples

See [`examples/`](./examples) for runnable scripts:

- `basic_trading.py` — REST orders, balances, history
- `async_trading.py` — concurrent fetches with `AsyncKlingEx`
- `websocket_stream.py` — public + user channels over WS
- `market_maker.py` — minimal market-making loop
- `withdrawals_example.py` — submit an on-chain withdrawal
- `pools_example.py` — query pools, add/remove liquidity
- `mining_pool_example.py` — pool stats + your workers/rewards

## License

MIT — see [LICENSE](./LICENSE).

## Support

- API docs: <https://klingex.io/support/api-docs>
- Issues: <https://github.com/Klingon-tech/klingex-py/issues>
- Email: <info@klingex.io>
