"""
Basic Trading Example

Demonstrates how to use the KlingEx SDK for basic trading operations.
"""

import os
from klingex import KlingEx, OrderSide, KlingExError

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
            print(f"  {market.symbol}: {market.base_asset_symbol}/{market.quote_asset_symbol} - {market.last_price}")

        # Get tickers (CMC format - uses underscore)
        print("\n=== BTC_USDT Ticker ===")
        ticker = client.markets.get_ticker("BTC_USDT")
        print(f"  Last Price: {ticker.last_price}")
        print(f"  Bid: {ticker.bid}")
        print(f"  Ask: {ticker.ask}")
        print(f"  High: {ticker.high}")
        print(f"  Low: {ticker.low}")

        # Get orderbook (market_id is an integer)
        print("\n=== Orderbook (top 3) ===")
        orderbook = client.markets.get_orderbook(market_id=1)
        print(f"  Market: {orderbook.base_symbol}-{orderbook.quote_symbol}")
        print("  Bids:")
        for bid in orderbook.bids[:3]:
            print(f"    {bid[0]} @ {bid[1]}")
        print("  Asks:")
        for ask in orderbook.asks[:3]:
            print(f"    {ask[0]} @ {ask[1]}")

        # ========================================
        # Authenticated Endpoints
        # ========================================

        # Get wallet balances
        print("\n=== Wallet Balances ===")
        try:
            balances = client.wallet.get_balances()
            for balance in balances:
                if int(balance.balance) > 0:
                    print(f"  {balance.symbol}: {balance.available} available, {balance.locked_balance} locked")
        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Place a limit buy order
        print("\n=== Placing Limit Buy Order ===")
        try:
            # Using human-readable values (default)
            # This will buy 0.001 BTC at $50,000
            order = client.orders.submit_order(
                symbol="BTC-USDT",
                trading_pair_id=1,
                side=OrderSide.BUY,
                quantity="0.001",  # 0.001 BTC
                price="50000",     # $50,000 per BTC
            )
            print(f"  Order ID: {order.order_id}")
            print(f"  Message: {order.message}")

            # Cancel the order (requires both order_id and trading_pair_id)
            print("\n=== Cancelling Order ===")
            result = client.orders.cancel_order(order.order_id, trading_pair_id=1)
            print(f"  Message: {result.message}")
            print(f"  Released: {result.released_balance}")

        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Get open orders
        print("\n=== Open Orders ===")
        try:
            open_orders = client.orders.get_open_orders()
            if open_orders:
                for order in open_orders[:5]:
                    print(f"  {order.id}: {order.side} {order.amount} @ {order.price}")
            else:
                print("  No open orders")
        except KlingExError as e:
            print(f"  Error: {e.message}")

        # Get all orders
        print("\n=== All Orders ===")
        try:
            all_orders = client.orders.get_orders(limit=5)
            for order in all_orders:
                print(f"  {order.id}: {order.side} {order.status} - {order.filled_amount}/{order.amount}")
        except KlingExError as e:
            print(f"  Error: {e.message}")


if __name__ == "__main__":
    main()
