"""Inspect AMM pools and (optionally) add/remove liquidity.

Pool listings are public. Position reads need an API key with the ``read``
scope. ``add_liquidity`` / ``remove_liquidity`` need the ``liquidity`` scope.

Amounts are smallest base units (matching the asset's decimals).
"""

import os

from klingex import KlingEx


def main() -> None:
    api_key = os.environ.get("KLINGEX_API_KEY")  # optional for read-only browsing
    client = KlingEx(api_key=api_key) if api_key else KlingEx()

    print("Public pools:")
    for pool in client.pools.list():
        print(
            f"  pool #{pool.id} {pool.base_symbol}/{pool.quote_symbol}"
            f"  reserves={pool.base_reserve}/{pool.quote_reserve}"
            f"  spot={pool.spot_price}"
        )

    if not api_key:
        print("\n(set KLINGEX_API_KEY to see your own positions or modify liquidity)")
        return

    print("\nYour LP positions:")
    positions = client.pools.positions()
    if not positions:
        print("  (none)")
        return

    for pos in positions:
        print(
            f"  pool #{pos.pool_id} {pos.base_symbol}/{pos.quote_symbol}"
            f"  share={pos.share_pct}%  net_earned={pos.net_earned_quote}"
        )

    # Example: chart-style history for the first position
    first = positions[0]
    history = client.pools.position_history(first.pool_id, days=14)
    print(f"\nLast {len(history.history)} snapshots for pool #{first.pool_id}")

    # Liquidity ops are commented out — uncomment to actually move balances.
    #
    # mint = client.pools.add_liquidity(
    #     pool_id=first.pool_id,
    #     base_amount_max="1000000",
    #     quote_amount_max="50000000",
    #     min_lp_tokens="1",
    # )
    # print(f"Minted {mint.lp_tokens_minted} LP tokens (bootstrap={mint.is_bootstrap})")
    #
    # burn = client.pools.remove_liquidity(
    #     pool_id=first.pool_id,
    #     lp_tokens=mint.lp_tokens_minted,
    #     min_base_out="0",
    #     min_quote_out="0",
    # )
    # print(f"Burned {burn.lp_tokens_burned}: got {burn.base_out} / {burn.quote_out}")


if __name__ == "__main__":
    main()
