"""Submit an on-chain withdrawal via the KlingEx API.

Requires an API key with the ``withdraw`` scope. Granting that scope at
key creation already passed 2FA, so the call itself is unattended.

NOTE: amounts are RAW INTEGER BASE UNITS (no decimal point). For BTC
(8 decimals) 0.001 BTC = 100_000 satoshis.
"""

import os

from klingex import KlingEx, KlingExError


def main() -> None:
    api_key = os.environ.get("KLINGEX_API_KEY")
    if not api_key:
        raise SystemExit("Set KLINGEX_API_KEY before running this example.")

    client = KlingEx(api_key=api_key)

    # Discover the asset_id + decimals from the wallet listing so we don't
    # hardcode anything specific to the env we're running against.
    btc = next((b for b in client.wallet.get_balances() if b.symbol == "BTC"), None)
    if btc is None:
        raise SystemExit("No BTC wallet for this user.")

    amount_human = "0.001"
    decimals = btc.decimals
    amount_raw = str(int(round(float(amount_human) * (10 ** decimals))))

    print(f"Submitting {amount_human} BTC = {amount_raw} sats withdrawal...")

    try:
        result = client.withdrawals.submit(
            symbol="BTC",
            asset_id=btc.id,
            amount=amount_raw,
            address="bc1qexampledontactuallyusethis000000000000",
        )
    except KlingExError as exc:
        print(f"Withdrawal rejected: {exc.status_code} {exc.message}")
        return

    print(f"Submitted: {result.withdrawal_id} ({result.message})")


if __name__ == "__main__":
    main()
