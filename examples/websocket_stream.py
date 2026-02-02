"""
WebSocket Streaming Example

Demonstrates real-time data streaming using the KlingEx WebSocket client.
"""

import asyncio
import os
from klingex import KlingExWebSocket

API_KEY = os.getenv("KLINGEX_API_KEY")


async def main():
    # Create WebSocket client
    ws = KlingExWebSocket(api_key=API_KEY)

    # Define message handlers
    def on_ticker(data):
        ticker = data.get("data", {})
        print(f"[Ticker] {ticker.get('symbol')}: {ticker.get('lastPrice')} "
              f"(24h: {ticker.get('changePercent24h')}%)")

    def on_orderbook(data):
        book = data.get("data", {})
        best_bid = book.get("bids", [[]])[0]
        best_ask = book.get("asks", [[]])[0]
        if best_bid and best_ask:
            print(f"[Orderbook] Best bid: {best_bid[0]} @ {best_bid[1]}, "
                  f"Best ask: {best_ask[0]} @ {best_ask[1]}")

    def on_trade(data):
        trade = data.get("data", {})
        print(f"[Trade] {trade.get('side').upper()} {trade.get('quantity')} @ {trade.get('price')}")

    def on_user_order(data):
        order = data.get("data", {})
        print(f"[Order Update] {order.get('id')}: {order.get('status')} - "
              f"Filled: {order.get('filledQuantity')}/{order.get('quantity')}")

    try:
        # Connect to WebSocket
        await ws.connect()
        print("Connected to KlingEx WebSocket")

        # Subscribe to public channels
        await ws.subscribe_ticker("BTC-USDT", on_ticker)
        await ws.subscribe_orderbook("BTC-USDT", on_orderbook)
        await ws.subscribe_trades("BTC-USDT", on_trade)

        # Subscribe to authenticated channels (if API key provided)
        if API_KEY:
            await ws.subscribe_user_orders(on_user_order)
            print("Subscribed to user order updates")

        print("Streaming data... Press Ctrl+C to stop\n")

        # Keep the connection alive
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await ws.close()
        print("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
