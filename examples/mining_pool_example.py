"""Show mining-pool stats and (with an API key) your workers / rewards."""

import os

from klingex import KlingEx


def main() -> None:
    api_key = os.environ.get("KLINGEX_API_KEY")
    client = KlingEx(api_key=api_key) if api_key else KlingEx()

    configs = client.mining_pool.get_configs()
    if not configs:
        print("No mining pools configured on this exchange.")
        return

    print("Pool configs:")
    for cfg in configs:
        print(f"  {cfg.symbol}: {cfg.name} (algo={cfg.algorithm})")

    target = configs[0].symbol
    stats = client.mining_pool.get_stats(symbol=target)
    print(f"\n{target} stats: hashrate={stats.pool_hashrate} miners={stats.miner_count}")

    blocks = client.mining_pool.get_blocks(symbol=target, limit=5)
    print(f"Recent {len(blocks)} {target} blocks:")
    for block in blocks:
        print(f"  #{block.height} status={block.status} reward={block.reward}")

    if not api_key:
        print("\n(set KLINGEX_API_KEY for personal workers/rewards/payouts)")
        return

    workers = client.mining_pool.get_my_workers(symbol=target)
    print(f"\nYour {target} workers: {len(workers.workers)} online")
    for worker in workers.workers[:5]:
        print(f"  {worker.name}: {worker.hashrate} ({worker.status})")

    rewards = client.mining_pool.get_my_rewards(symbol=target, limit=5)
    print(f"\nRecent {target} rewards:")
    for reward in rewards.rewards:
        print(f"  {reward.amount} at block #{reward.block_height}")


if __name__ == "__main__":
    main()
