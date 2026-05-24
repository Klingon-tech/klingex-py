"""KlingEx SDK types and pydantic models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(str, Enum):
    """Backend order statuses (no separate ``open`` state)."""

    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Base model (permissive: forward-compatible with new backend fields)
# ---------------------------------------------------------------------------
class _SDKBase(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# ---------------------------------------------------------------------------
# Markets / assets
# ---------------------------------------------------------------------------
class Market(_SDKBase):
    """Trading market/pair (matches backend ``markets.Market`` shape)."""

    id: int
    base_asset_id: int
    quote_asset_id: int
    min_trade_amount: str
    max_trade_amount: Optional[str] = None
    tick_size: str
    step_size: str
    maker_fee_rate: str
    taker_fee_rate: str
    price_decimals: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    base_asset_symbol: str
    base_asset_name: str
    quote_asset_symbol: str
    quote_asset_name: str
    base_decimals: int
    quote_decimals: int
    # Nullable in backend (no 24h activity yet)
    volume_24h: Optional[str] = None
    priceChange24h: Optional[str] = None
    last_price: Optional[str] = None
    volume_24h_human: Optional[str] = None

    @property
    def symbol(self) -> str:
        return f"{self.base_asset_symbol}-{self.quote_asset_symbol}"


class MarketInfo(_SDKBase):
    """Lightweight market-info response (``/api/market-info``)."""

    trading_pair_id: int
    base_symbol: str
    base_decimals: int
    quote_symbol: str
    quote_decimals: int
    min_trade_amount: str
    max_trade_amount: Optional[str] = None
    tick_size: str
    step_size: str
    maker_fee_rate: str
    taker_fee_rate: str
    price_decimals: int


class SparklinePoint(_SDKBase):
    time_bucket: datetime
    price: str


class MarketSparklinesResponse(_SDKBase):
    timeframe: str
    limit: int
    sparklines: Dict[str, List[SparklinePoint]]


class Asset(_SDKBase):
    """Asset listing entry (``/api/assets``)."""

    symbol: str
    name: str
    decimals: int
    is_crypto: bool
    chain_type: Optional[str] = None
    chain_id: Optional[int] = None
    evm_network: Optional[str] = None
    contract_address: Optional[str] = None
    is_active: bool
    withdrawal_enabled: bool
    website: Optional[str] = None
    twitter_url: Optional[str] = None
    discord_url: Optional[str] = None
    telegram_url: Optional[str] = None
    description: Optional[str] = None


class AssetInfo(_SDKBase):
    """Detailed asset info (``/api/asset-info/:id`` and ``/symbol/:symbol``)."""

    symbol: str
    name: str
    decimals: int
    is_crypto: bool
    chain_type: Optional[str] = None
    chain_id: Optional[int] = None
    evm_network: Optional[str] = None
    contract_address: Optional[str] = None
    explorer_url: Optional[str] = None
    is_active: bool
    withdrawal_enabled: bool
    min_deposit: Optional[str] = None
    min_withdrawal: Optional[str] = None
    withdrawal_fee: Optional[str] = None
    deposit_fee: Optional[str] = None
    deposit_fee_threshold: Optional[str] = None
    website: Optional[str] = None
    twitter_url: Optional[str] = None
    discord_url: Optional[str] = None
    telegram_url: Optional[str] = None
    description: Optional[str] = None


class Ticker(_SDKBase):
    """CMC/CoinGecko ticker shape (``/api/tickers``)."""

    ticker_id: str
    base_currency: str
    target_currency: str
    last_price: str
    base_volume: str
    target_volume: str
    bid: str
    ask: str
    high: str
    low: str


class OrderBook(_SDKBase):
    trading_pair_id: int
    base_symbol: str
    quote_symbol: str
    bids: List[List[Any]]
    asks: List[List[Any]]


class OHLCV(_SDKBase):
    time_bucket: datetime
    open_price: Optional[str] = None
    high_price: Optional[str] = None
    low_price: Optional[str] = None
    close_price: Optional[str] = None
    volume: Optional[str] = None
    number_of_trades: Optional[int] = None


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
class Order(_SDKBase):
    id: str
    trading_pair_id: int
    side: str
    type: str
    price: Optional[str] = None
    amount: str
    filled_amount: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderResponse(_SDKBase):
    """Response from ``POST /api/submit-order``."""

    message: str
    order_id: str = Field(alias="orderId")
    locked_amount: Optional[str] = Field(default=None, alias="lockedAmount")


class CancelOrderResponse(_SDKBase):
    message: str
    released_balance: Optional[str] = None


class CancelAllOrdersResponse(_SDKBase):
    """Response from ``POST /api/cancel-all-orders``."""

    message: str
    cancelled_count: int = Field(alias="cancelledCount")
    total_orders: int = Field(alias="totalOrders")
    cancelled_order_ids: List[str] = Field(default_factory=list, alias="cancelledOrderIds")
    total_released_balance: Optional[str] = Field(default=None, alias="totalReleasedBalance")


class OrderHistory(_SDKBase):
    id: str
    trading_pair_id: int
    base_symbol: str
    quote_symbol: str
    type: str
    side: str
    status: str
    price: Optional[str] = None
    amount: str
    filled_amount: str
    created_at: datetime
    updated_at: datetime
    human_price: Optional[str] = None
    human_amount: Optional[str] = None
    human_filled_amount: Optional[str] = None
    human_remaining: Optional[str] = None
    human_total: Optional[str] = None


class OrdersHistoryResponse(_SDKBase):
    orders: List[OrderHistory]
    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Wallets
# ---------------------------------------------------------------------------
class Balance(_SDKBase):
    id: int
    symbol: str
    name: str
    decimals: int
    balance: str
    locked_balance: str
    wallet_id: Optional[str] = None
    deposit_address: Optional[str] = None
    min_deposit: Optional[str] = None
    min_withdrawal: Optional[str] = None
    withdrawal_fee: Optional[str] = None

    @property
    def available(self) -> str:
        return str(int(self.balance) - int(self.locked_balance))

    @property
    def total(self) -> str:
        return self.balance


class WalletStatusCounts(_SDKBase):
    active: int = 0
    delayed: int = 0
    stale: int = 0
    never_synced: int = 0


class AssetSyncRow(_SDKBase):
    asset_id: int
    symbol: str
    name: str
    network_name: str
    chain_id: Optional[int] = None
    block_number: Optional[int] = None
    processed_at: Optional[datetime] = None
    sync_status: str
    seconds_since_last_sync: Optional[float] = None
    explorer_url: Optional[str] = None
    deposits_enabled: bool = True
    withdrawals_enabled: bool = True


class WalletChainGroup(_SDKBase):
    network_name: str
    chain_id: Optional[int] = None
    assets: List[AssetSyncRow] = Field(default_factory=list)


class WalletSystemStatus(_SDKBase):
    """Response from ``GET /api/wallets/status``."""

    overall_status: str
    system_health_percentage: int
    last_updated: datetime
    status_counts: WalletStatusCounts
    total_assets: int
    chain_groups: List[WalletChainGroup] = Field(default_factory=list)


class AssetSyncInfo(_SDKBase):
    current_block: Optional[int] = None
    last_processed_at: Optional[datetime] = None
    sync_status: str
    seconds_since_last_sync: Optional[float] = None


class AssetSyncStatus(_SDKBase):
    """Response from ``GET /api/wallets/status/:assetId``."""

    asset_id: int
    symbol: str
    name: str
    chain_type: Optional[str] = None
    network_name: str
    chain_id: Optional[int] = None
    contract_address: Optional[str] = None
    explorer_url: Optional[str] = None
    is_active: Optional[bool] = None
    withdrawal_enabled: bool = True
    deposit_confirms_required: int = 0
    sync_info: AssetSyncInfo


# ---------------------------------------------------------------------------
# Withdrawals
# ---------------------------------------------------------------------------
class WithdrawalSubmitResponse(_SDKBase):
    """Response from ``POST /api/submit-withdraw`` (API-key path)."""

    message: str
    withdrawal_id: str = Field(alias="withdrawalId")


# ---------------------------------------------------------------------------
# Liquidity pools
# ---------------------------------------------------------------------------
class Pool(_SDKBase):
    """Public pool listing entry (``GET /api/pools/list``)."""

    id: int
    base_symbol: str
    quote_symbol: str
    base_reserve: str
    quote_reserve: str
    base_decimals: int
    quote_decimals: int
    total_lp_tokens: str
    pool_fee_rate: str
    spot_price: Optional[str] = None
    is_public: bool = True
    deposits_paused: bool = False
    withdrawals_paused: bool = False


class PoolDetail(Pool):
    """Full pool detail (``GET /api/pools/:id``)."""

    k_value: Optional[str] = None
    min_liquidity: Optional[str] = None
    order_levels: Optional[int] = None
    active_orders: Optional[int] = None
    lp_position_count: Optional[int] = None


class LPPosition(_SDKBase):
    """A user's position in a pool (``GET /api/pools/positions``)."""

    pool_id: int
    base_symbol: str
    quote_symbol: str
    lp_token_balance: str
    base_deposited: str
    quote_deposited: str
    base_decimals: int
    quote_decimals: int
    base_value: Optional[str] = None
    quote_value: Optional[str] = None
    share_pct: Optional[str] = None
    base_earned: Optional[str] = None
    quote_earned: Optional[str] = None
    net_earned_quote: Optional[str] = None
    approx_fees_earned: Optional[str] = None


class PositionHistorySnapshot(_SDKBase):
    timestamp: datetime
    lp_token_balance: str
    base_value: str
    quote_value: str
    total_value_quote: str
    net_earned_quote: str
    share_pct: str
    spot_price: str


class PositionHistoryResponse(_SDKBase):
    pool_id: int
    base_symbol: str
    quote_symbol: str
    base_decimals: int
    quote_decimals: int
    history: List[PositionHistorySnapshot] = Field(default_factory=list)


class AddLiquidityResult(_SDKBase):
    pool_id: int
    base_used: str
    quote_used: str
    lp_tokens_minted: str
    is_bootstrap: bool
    total_lp_supply: str


class RemoveLiquidityResult(_SDKBase):
    pool_id: int
    lp_tokens_burned: str
    base_out: str
    quote_out: str
    total_lp_supply: str


# ---------------------------------------------------------------------------
# Mining pool
# ---------------------------------------------------------------------------
class MiningPoolConfig(_SDKBase):
    algorithm: str
    symbol: str
    stratum_port: int
    pool_fee_percent: float
    pool_hashrate: str
    min_difficulty: float


class MiningBlock(_SDKBase):
    id: int
    asset_id: int
    symbol: str
    block_height: int
    block_hash: str
    block_reward: str
    pool_fee: str
    confirmations: int
    required_confirmations: int
    status: str
    found_at: datetime
    matured_at: Optional[datetime] = None
    credited_at: Optional[datetime] = None
    asset_decimals: int


class MiningBlocksResponse(_SDKBase):
    blocks: List[MiningBlock] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class MiningStatsCurrent(_SDKBase):
    pool_hashrate: str
    network_hashrate: str
    network_difficulty: float
    online_workers: int
    active_miners: int
    block_height: int
    blocks_24h: Optional[int] = None
    current_effort: Optional[float] = None
    ttf_minutes: Optional[float] = None
    net_share: Optional[float] = None
    last_block_found: Optional[datetime] = None
    luck_24h: Optional[float] = None


class MiningStatsSnapshot(_SDKBase):
    timestamp: datetime
    pool_hashrate: str
    network_hashrate: str
    network_difficulty: float
    online_workers: int
    active_miners: int


class MiningStats(_SDKBase):
    symbol: str
    current: MiningStatsCurrent
    history: List[MiningStatsSnapshot] = Field(default_factory=list)


class MiningLeaderboardEntry(_SDKBase):
    user_id: str
    total_rewards: str
    reward_formatted: str
    blocks_found: int
    total_shares: int
    hashrate: str
    worker_count: int


class MiningLeaderboard(_SDKBase):
    symbol: str
    period: str
    miners: List[MiningLeaderboardEntry] = Field(default_factory=list)


class MiningWorker(_SDKBase):
    worker_name: str
    symbol: str
    hashrate_1m: str
    difficulty: float
    shares_accepted: int
    shares_rejected: int
    shares_stale: int
    is_online: bool
    last_share_at: Optional[datetime] = None
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None


class MiningWorkersResponse(_SDKBase):
    workers: List[MiningWorker] = Field(default_factory=list)


class MiningReward(_SDKBase):
    id: str
    block_id: int
    asset_id: int
    asset_symbol: str
    asset_name: str
    asset_decimals: int
    reward_amount: str
    reward_amount_formatted: str
    shares: int
    total_shares: int
    status: str
    created_at: datetime
    credited_at: Optional[datetime] = None
    block_height: int
    block_hash: str
    block_status: str
    confirmations: int
    required_confirmations: int
    found_at: datetime


class MiningRewardsResponse(_SDKBase):
    rewards: List[MiningReward] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


class MiningPayout(_SDKBase):
    id: str
    wallet_id: str
    reward_id: Optional[str] = None
    block_id: Optional[int] = None
    asset_id: int
    asset_symbol: str
    asset_name: str
    asset_decimals: int
    amount: str
    amount_formatted: str
    created_at: datetime
    block_height: Optional[int] = None
    block_hash: Optional[str] = None


class MiningPayoutsResponse(_SDKBase):
    payouts: List[MiningPayout] = Field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0


# ---------------------------------------------------------------------------
# Gift codes
# ---------------------------------------------------------------------------
class GiftCodeResponse(_SDKBase):
    """Response from ``POST /api/gift-codes``."""

    gift_code_id: str
    code: str
    formatted_code: str
    asset_id: int
    asset_symbol: str
    asset_decimals: int
    amount: str
    amount_formatted: str
    hide_amount: bool
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    new_balance: str


class BulkGiftCodeResponse(_SDKBase):
    """Response from ``POST /api/gift-codes/bulk``."""

    gift_codes: List[GiftCodeResponse] = Field(default_factory=list)
    total_amount: str
    total_amount_formatted: str
    count: int
    new_balance: str


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------
class InvoiceDenomination(_SDKBase):
    type: str = "crypto"
    currency: str
    amount: str
    decimals: Optional[int] = None


class PaymentOption(_SDKBase):
    asset_id: int
    symbol: str
    name: str
    chain_type: Optional[str] = None
    address: str
    expected_amount: str
    exchange_rate: str
    qr_code_data: Optional[str] = None


class InvoicePayment(_SDKBase):
    id: str
    asset_id: int
    symbol: str
    amount: str
    tx_hash: Optional[str] = None
    status: str
    confirmations: Optional[int] = None
    confirmations_required: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime


class Invoice(_SDKBase):
    id: str
    external_id: Optional[str] = None
    status: str
    denomination: Optional[InvoiceDenomination] = None
    denomination_type: Optional[str] = None
    denomination_currency: Optional[str] = None
    amount: Optional[str] = None
    payment_options: Optional[List[PaymentOption]] = None
    payments: Optional[List[InvoicePayment]] = None
    fee_rate_bps: Optional[int] = None
    fee_rate_percent: Optional[str] = None
    total_received: Optional[str] = None
    fee_amount: Optional[str] = None
    net_amount: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    buyer_email: Optional[str] = None
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    payment_page_url: Optional[str] = None


class InvoiceListResponse(_SDKBase):
    invoices: List[Invoice]
    total_count: int
    page: int
    page_size: int


class InvoiceFeeStats(_SDKBase):
    current_fee_rate_bps: int
    current_fee_rate_percent: str
    paid_invoice_count: int
    total_fees_collected: str
    total_net_amount: str


class InvoiceStatusResponse(_SDKBase):
    """Polled invoice status (public endpoint, no auth)."""
    invoice_id: str
    status: str
    total_paid_percent: float = 0.0
    payments: Optional[List[InvoicePayment]] = None
    paid_at: Optional[datetime] = None
    time_remaining_ms: int = 0


class PublicInvoice(_SDKBase):
    """Public payment-page view of an invoice (no auth)."""
    invoice_id: str
    status: str
    denomination: InvoiceDenomination
    description: Optional[str] = None
    merchant_name: str
    expires_at: datetime
    time_remaining_ms: int = 0
    payment_options: List[PaymentOption] = []
    payments_received: Optional[List[InvoicePayment]] = None
    total_paid_percent: float = 0.0


__all__ = [
    # Enums
    "OrderSide",
    "OrderType",
    "OrderStatus",
    # Markets / assets
    "Asset",
    "AssetInfo",
    "Market",
    "MarketInfo",
    "SparklinePoint",
    "MarketSparklinesResponse",
    "Ticker",
    "OrderBook",
    "OHLCV",
    # Orders
    "Order",
    "OrderResponse",
    "CancelOrderResponse",
    "CancelAllOrdersResponse",
    "OrderHistory",
    "OrdersHistoryResponse",
    # Wallets
    "Balance",
    "WalletSystemStatus",
    "WalletStatusCounts",
    "WalletChainGroup",
    "AssetSyncRow",
    "AssetSyncStatus",
    "AssetSyncInfo",
    # Withdrawals
    "WithdrawalSubmitResponse",
    # Pools
    "Pool",
    "PoolDetail",
    "LPPosition",
    "PositionHistorySnapshot",
    "PositionHistoryResponse",
    "AddLiquidityResult",
    "RemoveLiquidityResult",
    # Mining
    "MiningPoolConfig",
    "MiningBlock",
    "MiningBlocksResponse",
    "MiningStats",
    "MiningStatsCurrent",
    "MiningStatsSnapshot",
    "MiningLeaderboard",
    "MiningLeaderboardEntry",
    "MiningWorker",
    "MiningWorkersResponse",
    "MiningReward",
    "MiningRewardsResponse",
    "MiningPayout",
    "MiningPayoutsResponse",
    # Gift codes
    "GiftCodeResponse",
    "BulkGiftCodeResponse",
    # Invoices
    "InvoiceDenomination",
    "PaymentOption",
    "InvoicePayment",
    "Invoice",
    "InvoiceListResponse",
    "InvoiceFeeStats",
    "InvoiceStatusResponse",
    "PublicInvoice",
]
