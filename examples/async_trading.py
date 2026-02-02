"""
Async Trading Example

Demonstrates how to use the async KlingEx client for concurrent operations.
"""

import asyncio
import os
from klingex.client import AsyncKlingEx
from klingex import OrderSide, OrderType, KlingExError

API_KEY = os.getenv("KLINGEX_API_KEY", "your_api_key")


async def main():
    async with AsyncKlingEx(api_key=API_KEY) as client:
        # Fetch multiple markets concurrently
        print("=== Fetching Data Concurrently ===")

        markets_task = client.markets.get_markets()
        tickers_task = client.markets.get_tickers()
        balances_task = client.wallet.get_balances()

        # Wait for all tasks to complete
        markets, tickers, balances = await asyncio.gather(
            markets_task,
            tickers_task,
            balances_task,
            return_exceptions=True,
        )

        # Process results
        if isinstance(markets, list):
            print(f"  Found {len(markets)} markets")
        else:
            print(f"  Markets error: {markets}")

        if isinstance(tickers, list):
            print(f"  Got {len(tickers)} tickers")
        else:
            print(f"  Tickers error: {tickers}")

        if isinstance(balances, list):
            non_zero = [b for b in balances if float(b.total) > 0]
            print(f"  Found {len(non_zero)} non-zero balances")
        else:
            print(f"  Balances error: {balances}")

        # Place multiple orders concurrently
        print("\n=== Placing Multiple Orders ===")
        try:
            orders = await asyncio.gather(
                client.orders.submit_order(
                    market_id="BTC-USDT",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity="0.001",
                    price="40000",
                ),
                client.orders.submit_order(
                    market_id="ETH-USDT",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity="0.01",
                    price="2000",
                ),
                return_exceptions=True,
            )

            for order in orders:
                if isinstance(order, Exception):
                    print(f"  Order failed: {order}")
                else:
                    print(f"  Order {order.order_id}: {order.status}")

        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Cancel all orders
        print("\n=== Cancelling All Orders ===")
        try:
            result = await client.orders.cancel_all_orders()
            print(f"  Result: {result}")
        except KlingExError as e:
            print(f"  Error: {e.message}")


if __name__ == "__main__":
    asyncio.run(main())
