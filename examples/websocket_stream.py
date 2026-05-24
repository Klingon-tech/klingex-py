"""Real-time market + user data over the KlingEx WebSocket.

Public market data needs no auth. User channels (orders, balance,
trades, ...) require an API key with the ``read`` scope. The
``connect()`` call waits for the server's ``auth_result`` reply before
returning, so user subscriptions placed immediately afterwards are
guaranteed to be authenticated.
"""

import asyncio
import os

from klingex import KlingExWebSocket

API_KEY = os.getenv("KLINGEX_API_KEY")


async def main() -> None:
    ws = KlingExWebSocket(api_key=API_KEY)

    def on_market(msg):
        # Single subscription delivers ticker + orderbook + trades for the
        # pair. Each message carries a `type` field identifying which one.
        kind = msg.get("type")
        market = msg.get("market")
        if kind == "ticker":
            print(f"[ticker {market}] last={msg.get('last_price')}")
        elif kind == "orderbook":
            bids, asks = msg.get("bids") or [], msg.get("asks") or []
            if bids and asks:
                print(f"[orderbook {market}] bid {bids[0]} | ask {asks[0]}")
        elif kind in ("trade", "trades"):
            print(f"[trade {market}] {msg.get('side')} {msg.get('amount')} @ {msg.get('price')}")

    def on_orders(msg):
        print(f"[order] {msg.get('id')} status={msg.get('status')} "
              f"filled={msg.get('filled_amount')}/{msg.get('amount')}")

    def on_balance(msg):
        print(f"[balance] {msg.get('symbol')}: {msg.get('balance')} "
              f"(locked={msg.get('locked_balance')})")

    try:
        await ws.connect()
        print("Connected.")

        await ws.subscribe_market("BTC-USDT", on_market)

        if API_KEY:
            await ws.subscribe_user("orders", on_orders)
            await ws.subscribe_user("balance", on_balance)  # NOTE: singular
            print("Authenticated; streaming user channels too.")

        print("Streaming... Ctrl+C to stop.\n")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        await ws.close()


if __name__ == "__main__":
    asyncio.run(main())
