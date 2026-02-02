"""
Basic Trading Example

Demonstrates how to use the KlingEx SDK for basic trading operations.
"""

import os
from klingex import KlingEx, OrderSide, OrderType, KlingExError

# Initialize client with API key
API_KEY = os.getenv("KLINGEX_API_KEY", "your_api_key")


def main():
    # Create client instance
    with KlingEx(api_key=API_KEY) as client:
        # ========================================
        # Public Endpoints (no auth required)
        # ========================================

        # Get all available markets
        print("=== Available Markets ===")
        markets = client.markets.get_markets()
        for market in markets[:5]:  # Show first 5
            print(f"  {market.symbol}: {market.base_asset}/{market.quote_asset}")

        # Get ticker for BTC-USDT
        print("\n=== BTC-USDT Ticker ===")
        ticker = client.markets.get_ticker("BTC-USDT")
        print(f"  Last Price: {ticker.last_price}")
        print(f"  24h Change: {ticker.change_percent_24h}%")
        print(f"  24h Volume: {ticker.volume_24h}")

        # Get orderbook
        print("\n=== BTC-USDT Orderbook (top 5) ===")
        orderbook = client.markets.get_orderbook("BTC-USDT", depth=5)
        print("  Bids:")
        for bid in orderbook.bids[:3]:
            print(f"    {bid.price} @ {bid.quantity}")
        print("  Asks:")
        for ask in orderbook.asks[:3]:
            print(f"    {ask.price} @ {ask.quantity}")

        # ========================================
        # Authenticated Endpoints
        # ========================================

        # Get wallet balances
        print("\n=== Wallet Balances ===")
        try:
            balances = client.wallet.get_balances()
            for balance in balances:
                if float(balance.total) > 0:
                    print(f"  {balance.symbol}: {balance.available} available, {balance.locked} locked")
        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Place a limit buy order
        print("\n=== Placing Limit Buy Order ===")
        try:
            # Using human-readable values (default)
            # This will buy 0.001 BTC at $50,000
            order = client.orders.submit_order(
                market_id="BTC-USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity="0.001",  # 0.001 BTC
                price="50000",     # $50,000 per BTC
            )
            print(f"  Order ID: {order.order_id}")
            print(f"  Status: {order.status}")

            # Get order details
            order_details = client.orders.get_order(order.order_id)
            print(f"  Filled: {order_details.filled_quantity}/{order_details.quantity}")

            # Cancel the order
            print("\n=== Cancelling Order ===")
            result = client.orders.cancel_order(order.order_id)
            print(f"  Result: {result}")

        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Get open orders
        print("\n=== Open Orders ===")
        try:
            open_orders = client.orders.get_open_orders()
            if open_orders:
                for order in open_orders[:5]:
                    print(f"  {order.id}: {order.side} {order.quantity} @ {order.price}")
            else:
                print("  No open orders")
        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Get order history
        print("\n=== Order History ===")
        try:
            history = client.orders.get_order_history(limit=5)
            for order in history:
                print(f"  {order.id}: {order.side} {order.status} - {order.filled_quantity}/{order.quantity}")
        except KlingExError as e:
            print(f"  Error: {e.message}")


if __name__ == "__main__":
    main()
