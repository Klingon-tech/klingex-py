"""
Simple Market Maker Example

Demonstrates a basic market-making strategy using the KlingEx SDK.
WARNING: This is for educational purposes only. Do not use in production
without proper risk management.
"""

import asyncio
import os
from decimal import Decimal
from klingex.client import AsyncKlingEx
from klingex import KlingExWebSocket, OrderSide, OrderType, KlingExError

API_KEY = os.getenv("KLINGEX_API_KEY", "your_api_key")
API_SECRET = os.getenv("KLINGEX_API_SECRET", "your_api_secret")

# Configuration
MARKET_ID = "BTC-USDT"
SPREAD_PERCENT = Decimal("0.002")  # 0.2% spread
ORDER_SIZE = "0.001"  # BTC per side
UPDATE_INTERVAL = 5  # seconds


class SimpleMarketMaker:
    def __init__(self, client: AsyncKlingEx, market_id: str):
        self.client = client
        self.market_id = market_id
        self.current_price: Decimal | None = None
        self.buy_order_id: str | None = None
        self.sell_order_id: str | None = None
        self.running = False

    async def update_price(self, price: str):
        """Update the mid price from ticker"""
        self.current_price = Decimal(price)

    async def cancel_existing_orders(self):
        """Cancel any existing orders"""
        tasks = []
        if self.buy_order_id:
            tasks.append(self.client.orders.cancel_order(self.buy_order_id))
            self.buy_order_id = None
        if self.sell_order_id:
            tasks.append(self.client.orders.cancel_order(self.sell_order_id))
            self.sell_order_id = None

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def place_orders(self):
        """Place new buy and sell orders around the current price"""
        if not self.current_price:
            return

        # Calculate bid and ask prices
        bid_price = self.current_price * (1 - SPREAD_PERCENT / 2)
        ask_price = self.current_price * (1 + SPREAD_PERCENT / 2)

        # Round to 2 decimal places for USDT
        bid_price_str = str(bid_price.quantize(Decimal("0.01")))
        ask_price_str = str(ask_price.quantize(Decimal("0.01")))

        print(f"Placing orders: BUY @ {bid_price_str}, SELL @ {ask_price_str}")

        try:
            # Place both orders concurrently
            buy_result, sell_result = await asyncio.gather(
                self.client.orders.submit_order(
                    market_id=self.market_id,
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity=ORDER_SIZE,
                    price=bid_price_str,
                ),
                self.client.orders.submit_order(
                    market_id=self.market_id,
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    quantity=ORDER_SIZE,
                    price=ask_price_str,
                ),
                return_exceptions=True,
            )

            if not isinstance(buy_result, Exception):
                self.buy_order_id = buy_result.order_id
                print(f"  Buy order placed: {self.buy_order_id}")
            else:
                print(f"  Buy order failed: {buy_result}")

            if not isinstance(sell_result, Exception):
                self.sell_order_id = sell_result.order_id
                print(f"  Sell order placed: {self.sell_order_id}")
            else:
                print(f"  Sell order failed: {sell_result}")

        except KlingExError as e:
            print(f"Error placing orders: {e.message}")

    async def run(self):
        """Main market maker loop"""
        self.running = True
        print(f"Starting market maker for {self.market_id}")
        print(f"Spread: {SPREAD_PERCENT * 100}%, Order size: {ORDER_SIZE}")
        print("-" * 50)

        while self.running:
            try:
                # Get current ticker
                ticker = await self.client.markets.get_ticker(self.market_id)
                await self.update_price(ticker.last_price)

                # Cancel existing orders and place new ones
                await self.cancel_existing_orders()
                await self.place_orders()

                # Wait before next update
                await asyncio.sleep(UPDATE_INTERVAL)

            except KlingExError as e:
                print(f"Error: {e.message}")
                await asyncio.sleep(UPDATE_INTERVAL)
            except Exception as e:
                print(f"Unexpected error: {e}")
                await asyncio.sleep(UPDATE_INTERVAL)

    async def stop(self):
        """Stop the market maker and cancel all orders"""
        self.running = False
        await self.cancel_existing_orders()
        print("Market maker stopped")


async def main():
    async with AsyncKlingEx(api_key=API_KEY, api_secret=API_SECRET) as client:
        # Check balances first
        print("=== Checking Balances ===")
        try:
            balances = await client.wallet.get_balances()
            for balance in balances:
                if balance.symbol in ["BTC", "USDT"]:
                    print(f"  {balance.symbol}: {balance.available} available")
        except KlingExError as e:
            print(f"  Error: {e.message}")
            return

        print()

        # Create and run market maker
        mm = SimpleMarketMaker(client, MARKET_ID)

        try:
            await mm.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
            await mm.stop()


if __name__ == "__main__":
    print("=" * 50)
    print("SIMPLE MARKET MAKER - EDUCATIONAL EXAMPLE")
    print("WARNING: Do not use in production!")
    print("=" * 50)
    print()

    asyncio.run(main())
